#!/usr/bin/python3
import os
import os.path
import sqlite3


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
