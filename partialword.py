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

INSERT_LOW_NGRAM_DML = '''
INSERT INTO ngram (words, freq) VALUES (?, ?);
'''

#try delete last
DELETE_HIGH_NGRAM_DML = '''
DELETE FROM ngram WHERE words = ?;
'''


#sqlite full text search section
CREATE_NGRAM_FTS_DDL = '''
CREATE VIRTUAL TABLE ngram_fts USING fts3 (words TEXT NOT NULL, freq INTEGER NOT NULL);
'''

POPULATE_NGRAM_FTS_DML = '''
INSERT INTO ngram_fts (words, freq) SELECT words, freq FROM ngram WHERE freq > ?;
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


def createNgramTableClone(conn, threshold):
    print("creating ngram fts table...")

    cur = conn.cursor()

    cur.execute(CREATE_NGRAM_FTS_DDL)
    cur.execute(POPULATE_NGRAM_FTS_DML, (threshold, ))

    conn.commit()


def dropNgramTableClone(conn):
    print("dropping ngram fts table...")
    cur = conn.cursor()

    cur.execute(DROP_NGRAM_FTS_DML)

    conn.commit()


#from 2-gram.db
def getPartialWordList(conn, threshold):
    #print(threshold)

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


def getMatchedItems(cur, words):
    #print(words)
    (prefix, postfix) = words

    matched_list = []
    sep = config.getWordSep()
    words_str = '"' + sep + prefix + sep + postfix + sep + '"'
    #print(words_str)

    rows = cur.execute(SELECT_MERGE_HIGH_NGRAM_DML, (words_str, )).fetchall()

    for row in rows:
        (words, freq) = row
        matched_list.append((words, freq))

    return matched_list


def doCombineWord(high_cur, low_cur, words):
    #print(words)
    (prefix, postfix) = words

    sep = config.getWordSep()

    matched_items = getMatchedItems(high_cur, words)
    words_str = sep + prefix + sep + postfix + sep
    #print(words_str)

    for item in matched_items:
        (matched_words_str, matched_freq) = item
        assert words_str in matched_words_str
        merged_str = sep + prefix + postfix + sep

        (left, middle, right) = matched_words_str.partition(words_str)
        while middle != '':
            merged_words_str = left + merged_str + right

            #print(matched_words_str), print(merged_words_str)
            assert len(matched_words_str) == len(merged_words_str) + 1

            #do combine
            rowcount = low_cur.execute(UPDATE_LOW_NGRAM_DML, \
                                           (matched_freq, merged_words_str)).rowcount
            #print(rowcount)
            assert rowcount <= 1

            if 0 == rowcount:
                low_cur.execute(INSERT_LOW_NGRAM_DML, \
                                    (merged_words_str, matched_freq))

                rowcount = high_cur.execute(DELETE_HIGH_NGRAM_DML, \
                                                (merged_words_str, )).rowcount
                assert rowcount <= 1

            (partial_left, middle, right) = right.partition(words_str)
            left = left + middle + partial_left


def recognizePartialWord(workdir, threshold):
    print(workdir, threshold)

    iternum = 0
    maxIter = config.getMaximumIteration()

    bigram_set = set([])

    filename = config.getPartialWordFileName()
    filepath = workdir + os.sep + filename
    partialwordfile = open(filepath, "w")

    while iternum < maxIter :
        print("pass ", iternum)

        length = 2
        filename = config.getNgramFileName(length)
        filepath = workdir + os.sep + filename

        conn = sqlite3.connect(filepath)
        partial_words_list = getPartialWordList(conn, threshold)
        conn.close()

        changed_num = 0
        for item in partial_words_list:
            (merged_word, prefix, postfix, freq) = item
            if merged_word in words_set :
                continue
            if (prefix, postfix) in bigram_set:
                continue
            changed_num = changed_num + 1

        if 0 == changed_num:
            break;

        for item in partial_words_list:
            (merged_word, prefix, postfix, freq) = item
            if merged_word in words_set:
                continue
            if (prefix, postfix) in bigram_set:
                continue
            oneline = "\t".join((merged_word, prefix, postfix, str(freq)))
            partialwordfile.writelines([oneline, os.linesep])

        for i in range(N, 1, -1):
            #high n-gram
            filename = config.getNgramFileName(i)
            filepath = workdir + os.sep + filename
            high_conn = sqlite3.connect(filepath)
            high_cur = high_conn.cursor()

            #low n-gram
            filename = config.getNgramFileName(i - 1)
            filepath = workdir + os.sep + filename
            low_conn = sqlite3.connect(filepath)
            low_cur = low_conn.cursor()

            dropNgramTableClone(high_conn)
            createNgramTableClone(high_conn, threshold)

            for item in partial_words_list:
                (merged_word, prefix, postfix, freq) = item

                if merged_word in words_set :
                    continue

                if (prefix, postfix) in bigram_set:
                    continue

                print(merged_word, prefix, postfix, freq, i)
                doCombineWord(high_cur, low_cur, (prefix, postfix))

            high_conn.commit(), low_conn.commit()
            dropNgramTableClone(high_conn)
            high_conn.close(), low_conn.close()

        for item in partial_words_list:
            (merged_word, prefix, postfix, freq) = item
            bigram_set.add((prefix, postfix))

        iternum = iternum + 1

    partialwordfile.close()
    print(workdir, 'done')


print("loading...")
load_words(config.getWordsListFileName())
#print(words_set)

