#!/usr/bin/python3
import os
import sqlite3
from argparse import ArgumentParser
import utils
from myconfig import MyConfig


SELECT_PARTIAL_WORD_DML = '''
SELECT words, freq FROM ngram WHERE freq > ?;
'''

#try insert first
INSERT_LOW_NGRAM_DML = '''
INSERT INTO ngram (words, freq) VALUES (?, ?);
'''

UPDATE_LOW_NGRAM_DML = '''
UPDATE ngram SET freq = freq + ? WHERE words = ?;
'''

#try delete last
DELETE_HIGH_NGRAM_DML = '''
DELETE FROM ngram WHERE words = ?;
'''
#assert rowcount <= 1


#sqlite full text search section
CREATE_NGRAM_FTS_DDL = '''
CREATE VIRTUAL TABLE ngram_fts USING fts3 (words TEXT NOT NULL, freq INTEGER NOT NULL);
'''

POPULATE_NGRAM_FTS_DML = '''
INSERT INTO ngram_fts (words, freq) SELECT words, freq FROM ngram;
'''

DROP_NGRAM_FTS_DML = '''
DROP TABLE IF EXISTS ngram_fts;
'''

SELECT_MERGE_HIGH_NGRAM_DML = '''
SELECT words, freq FROM ngram_fts WHERE words MATCH ?;
'''

config = MyConfig()

#maximum combine number
N = config.getMaximumCombineNumber()

#change cwd to the word recognizer directory
words_dir = config.getWordRecognizerDir()
os.chdir(words_dir)
#chdir done


#load existing words
words_set = set([])

def load_words(filename):
    wordlistfile = open(filename, "r")

    for oneline in wordlistfile.readlines():
        oneline = oneline.rstrip(os.linesep)

        if len(oneline) == 0:
            continue

        word = oneline

        words_set.add(word)

    wordlistfile.close()


load_words(config.getWordsListFileName())
#print(words_set)


def createNgramTableClone(conn):
    cur = conn.cursor()

    cur.execute(CREATE_NGRAM_FTS_DDL)
    cur.execute(POPULATE_NGRAM_FTS_DML)

    conn.commit()


def dropNgramTableClone(conn):
    cur = conn.cursor()

    cur.execute(DROP_NGRAM_FTS_DML)

    conn.commit()
