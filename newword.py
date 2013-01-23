#!/usr/bin/python3
import os
import os.path
import sqlite3
from argparse import ArgumentParser
from math import log
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
    print(freqs)

    totalfreq = sum(freqs)
    freqs = [ freq / float(totalfreq) for freq in freqs ]
    assert 1 == sum(freqs)

    entropy = sum([ - freq * log(freq) for freq in freqs ])
    print(entropy)
    return entropy




############################################################
#                Get Threshold Pass                        #
############################################################


############################################################
#                  Get Word Pass                           #
############################################################
