#!/usr/bin/python3
import os
import os.path
import sqlite3
from argparse import ArgumentParser
from operator import itemgetter
from math import log
from sys import float_info
import utils
from myconfig import MyConfig
from dirwalk import walkIndex


config = MyConfig()

#change cwd to the word recognizer directory
words_dir = config.getWordRecognizerDir()
os.chdir(words_dir)
#chdir done


############################################################
#                Create Bigram Database                    #
############################################################


CREATE_BIGRAM_DDL = '''
CREATE TABLE bigram (
      prefix TEXT NOT NULL,
      postfix TEXT NOT NULL,
      freq INTEGER NOT NULL
      );
'''

CREATE_BIGRAM_PREFIX_INDEX_DDL = '''
CREATE INDEX bigram_prefix_index on bigram(prefix);
'''

CREATE_BIGRAM_POSTFIX_INDEX_DDL = '''
CREATE INDEX bigram_postfix_index on bigram(postfix);
'''

SELECT_ALL_NGRAM_DML = '''
SELECT words, freq FROM ngram;
'''

INSERT_BIGRAM_DML = '''
INSERT INTO bigram(prefix, postfix, freq) VALUES (?, ?, ?);
'''


def createBigramSqlite(workdir):
    print(workdir, 'create bigram')

    filename = config.getBigramFileName()
    filepath = workdir + os.sep + filename
    print(filepath)

    if os.access(filepath, os.F_OK):
        os.unlink(filepath)

    conn = sqlite3.connect(filepath)
    cur = conn.cursor()
    cur.execute(CREATE_BIGRAM_DDL)
    cur.execute(CREATE_BIGRAM_PREFIX_INDEX_DDL)
    cur.execute(CREATE_BIGRAM_POSTFIX_INDEX_DDL)
    conn.commit()
    if conn:
        conn.close()


def populateBigramSqlite(workdir):
    print(workdir, 'populate bigram')

    sep = config.getWordSep()

    filename = config.getBigramFileName()
    filepath = workdir + os.sep + filename

    bigram_conn = sqlite3.connect(filepath)
    bigram_cur = bigram_conn.cursor()

    length = 2
    filename = config.getNgramFileName(length)
    filepath = workdir + os.sep + filename

    ngram_conn = sqlite3.connect(filepath)
    ngram_cur = ngram_conn.cursor()

    #begin processing
    rows = ngram_cur.execute(SELECT_ALL_NGRAM_DML).fetchall()
    for row in rows:
        (words_str, freq) = row

        words = words_str.strip(sep).split(sep, 1)
        assert len(words) == length

        (prefix, postfix) = words

        bigram_cur.execute(INSERT_BIGRAM_DML, (prefix, postfix, freq))
        #print(prefix, postfix, freq)

    bigram_conn.commit()
    ngram_conn.commit()

    if bigram_conn:
        bigram_conn.close()
    if ngram_conn:
        ngram_conn.close()


############################################################
#             Information Entropy Model                    #
############################################################

def computeEntropy(freqs):
    #print(freqs)

    totalfreq = sum(freqs)
    freqs = [ freq / float(totalfreq) for freq in freqs ]
    assert abs(1 - sum(freqs)) < len(freqs) * float_info.epsilon

    entropy = - sum([ freq * log(freq) for freq in freqs ])
    return entropy


############################################################
#                Get Threshold Pass                        #
############################################################


SELECT_PREFIX_DML = '''
SELECT prefix, freq FROM bigram WHERE postfix = ? ;
'''

SELECT_POSTFIX_DML = '''
SELECT postfix, freq FROM bigram WHERE prefix = ? ;
'''


def computePrefixEntropy(cur, word):
    rows = cur.execute(SELECT_PREFIX_DML, (word, )).fetchall()
    if 0 == len(rows):
        return 0.

    freqs = []
    for row in rows:
        (prefix, freq) = row
        assert freq >= 1
        freqs.append(freq)

    return computeEntropy(freqs)


def computePostfixEntropy(cur, word):

    rows = cur.execute(SELECT_POSTFIX_DML, (word, )).fetchall()
    if 0 == len(rows):
        return 0.

    freqs = []
    for row in rows:
        (postfix, freq) = row
        assert freq >= 1
        freqs.append(freq)

    return computeEntropy(freqs)


def computeThreshold(conn, tag):
    cur = conn.cursor()

    wordswithentropy = []
    wordlistfile = open(config.getWordsListFileName(), "r")

    for oneline in wordlistfile.readlines():
        oneline = oneline.rstrip(os.linesep)

        if len(oneline) == 0:
            continue

        word = oneline

        entropy = 0.
        if "prefix" == tag:
            entropy = computePrefixEntropy(cur, word)
        elif "postfix" == tag:
            entropy = computePostfixEntropy(cur, word)
        else:
            raise "invalid tag value."

        #print(word, entropy)

        if entropy < config.getMinimumEntropy():
            continue

        wordswithentropy.append((word, entropy))

    wordlistfile.close()

    conn.commit()

    #ascending sort
    wordswithentropy.sort(key=itemgetter(1))
    pos = int(len(wordswithentropy) * config.getNewWordThreshold())
    (word, threshold) = wordswithentropy[-pos]
    print(word, tag, threshold)
    return threshold


############################################################
#                  Get Word Pass                           #
############################################################

def filterPartialWord(workdir, conn, prethres, postthres):
    words_set = set([])
    cur = conn.cursor()

    filepath = workdir + os.sep + config.getPartialWordFileName()
    partialwordfile = open(filepath, "r")

    filepath = workdir + os.sep + config.getNewWordFileName()
    newwordfile = open(filepath, "w")

    for oneline in partialwordfile.readlines():
        oneline = oneline.rstrip(os.linesep)

        if len(oneline) == 0:
            continue

        (word, prefix, postfix, freq) = oneline.split(None, 3)

        if word in words_set:
            continue

        entropy = computePrefixEntropy(cur, word)
        if entropy < prethres:
            continue
        entropy = computePostfixEntropy(cur, word)
        if entropy < postthres:
            continue

        print(word)
        newwordfile.writelines([word, os.linesep])
        words_set.add(word)

    newwordfile.close()
    partialwordfile.close()
    conn.commit()


############################################################
#                  Handle Index                            #
############################################################

def handleOneIndex(indexpath, subdir, indexname):
    print(indexpath, subdir, indexname)

    indexstatuspath = indexpath + config.getStatusPostfix()
    indexstatus = utils.load_status(indexstatuspath)
    if not utils.check_epoch(indexstatus, 'PartialWord'):
        raise utils.EpochError('Please partial word first.\n')
    if utils.check_epoch(indexstatus, 'NewWord'):
        return

    workdir = config.getWordRecognizerDir() + os.sep + \
        subdir + os.sep + indexname
    print(workdir)

    createBigramSqlite(workdir)
    populateBigramSqlite(workdir)

    filename = config.getBigramFileName()
    filepath = workdir + os.sep + filename

    conn = sqlite3.connect(filepath)

    prethres = computeThreshold(conn, "prefix")
    indexstatus['NewWordPrefixThreshold'] = prethres
    postthres = computeThreshold(conn, "postfix")
    indexstatus['NewWordPostfixThreshold'] = postthres

    utils.store_status(indexstatuspath, indexstatus)

    filterPartialWord(workdir, conn, prethres, postthres)

    conn.commit()
    if conn:
        conn.close()

    #sign epoch
    utils.sign_epoch(indexstatus, 'NewWord')
    utils.store_status(indexstatuspath, indexstatus)


if __name__ == '__main__':
    parser = ArgumentParser(description='Recognize new words.')
    parser.add_argument('--indexdir', action='store', \
                            help='index directory', \
                            default=config.getTextIndexDir())


    args = parser.parse_args()
    print(args)
    walkIndex(handleOneIndex, args.indexdir)
    print('done')
