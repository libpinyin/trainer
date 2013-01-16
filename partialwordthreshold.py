#!/usr/bin/python3
import os
import sqlite3
from argparse import ArgumentParser
from operator import itemgetter
import utils
from myconfig import MyConfig
from dirwalk import walkIndex

SELECT_WORD_DML = '''
SELECT freq from ngram where words = ?;
'''

config = MyConfig()

#change cwd to the word recognizer directory
words_dir = config.getWordRecognizerDir()
os.chdir(words_dir)
#chdir done


def getWordFrequency(conn, word):
    sep = config.getWordSep()
    word_str = sep + word + sep

    cur = conn.cursor()
    row = cur.execute(SELECT_WORD_DML, (word_str, )).fetchone()

    if None == row:
        return 0
    else:
        freq = row[0]
        return freq


def computeThreshold(conn):
    wordswithfreq = []
    wordlistfile = open(config.getWordsListFileName(), "r")

    for oneline in wordlistfile.readlines():
        oneline = oneline.rstrip(os.linesep)

        if len(oneline) == 0:
            continue

        word = oneline

        freq = getWordFrequency(conn, word)

        if freq < config.getMinimumOccurrence():
            continue

        wordswithfreq.append((word, freq))

    wordlistfile.close()

    #ascending sort
    wordswithfreq.sort(key=itemgetter(1))
    pos = int(len(wordswithfreq) * config.getPartialWordThreshold())
    (word, threshold) = wordswithfreq[-pos]
    print(word, threshold)
    return threshold


def handleOneIndex(indexpath, subdir, indexname):
    print(indexpath, subdir, indexname)

    indexstatuspath = indexpath + config.getStatusPostfix()
    indexstatus = utils.load_status(indexstatuspath)
    if not utils.check_epoch(indexstatus, 'Populate'):
        raise utils.EpochError('Please populate first.\n')
    if utils.check_epoch(indexstatus, 'PartialWordThreshold'):
        return

    workdir = config.getWordRecognizerDir() + os.sep + \
        subdir + os.sep + indexname
    print(workdir)

    length = 1

    filename = config.getNgramFileName(length)
    filepath = workdir + os.sep + filename

    conn = sqlite3.connect(filepath)

    threshold = computeThreshold(conn)
    indexstatus['PartialWordThreshold'] = threshold

    conn.commit()
    if conn:
        conn.close()

    #sign epoch
    utils.sign_epoch(indexstatus, 'PartialWordThreshold')
    utils.store_status(indexstatuspath, indexstatus)


if __name__ == '__main__':
    parser = ArgumentParser(description='Partial word threshold.')
    parser.add_argument('--indexdir', action = 'store', \
                            help='index directory', \
                            default=os.path.join(config.getTextDir(), 'index'))

    args = parser.parse_args()
    print(args)
    walkIndex(handleOneIndex, args.indexdir)
    print('done')
