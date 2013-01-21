#!/usr/bin/python3
import os
import sqlite3
from argparse import ArgumentParser
import utils
from myconfig import MyConfig


SELECT_PARTIAL_WORD_DML = '''
SELECT words, freq FROM ngram WHERE freq > ?;
'''

#try update first to get affected row count
UPDATE_LOW_NGRAM_DML = '''
UPDATE ngram SET freq = freq + ? WHERE words = ?;
'''
#assert rowcount <= 1

INSERT_LOW_NGRAM_DML = '''
INSERT INTO ngram (words, freq) VALUES (?, ?);
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


#from 2-gram.db
def getPartialWordList(conn, threshold):
    print(threshold)

    words_list = []
    sep = config.getWordSep()

    cur = conn.cursor()
    rows = cur.execute(SELECT_PARTIAL_WORD_DML, (threshold, )).fetchall()

    for row in rows:
        (words_str, freq) = row
        (prefix, postfix) = words_str.strip(sep).split(sep, 1)
        merged_word = prefix + postfix
        words_list.append((merged_word, prefix, postfix, freq))

    conn.commit()
    return words_list


def getMatchedItems(conn, words):
    print(words)
    (prefix, postfix) = words

    matched_list = []
    sep = config.getWordSep()
    words_str = '"' + sep + prefix + sep + postfix + sep + '"'
    print(words_str)

    cur = conn.cursor()
    rows = cur.execute(SELECT_MERGE_HIGH_NGRAM_DML, (words_str, )).fetchall()

    for row in rows:
        (words, freq) = row
        matched_list.append((words, freq))

    conn.commit()
    return matched_list
