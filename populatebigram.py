#!/usr/bin/sqlite3
import os
import os.path
import sqlite3
from argparse import ArgumentParser
import utils
from myconfig import MyConfig


CREATE_BIGRAM_DDL = '''
CREATE TABLE bigram (
      prefix TEXT NOT NULL,
      postfix TEXT NOT NULL,
      freq INTEGER NOT NULL
      );
'''

SELECT_ALL_NGRAM_DML = '''
SELECT words, freq FROM ngram;
'''

DELETE_BIGRAM_DML = '''
DELETE FROM bigram;
'''

INSERT_BIGRAM_DML = '''
INSERT INTO bigram(prefix, postfix, freq) VALUES (?, ?, ?);
'''


config = MyConfig()

#change cwd to the word recognizer directory
words_dir = config.getWordRecognizerDir()
os.chdir(words_dir)
#chdir done


def handleError(error):
    sys.exit(error)


def createBigramSqlite(indexpath, workdir):
    print(indexpath, workdir, 'create bigram')
    length = 2

    filename = config.getNgramFileName(length)
    filepath = workdir + os.sep + filename
    print(filepath)

    if os.access(filepath, os.F_OK):
        os.unlink(filepath)

    conn = sqlite3.connect(filepath)
    cur = conn.cursor()
    cur.execute(CREATE_BIGRAM_DDL)
    conn.commit()
    if conn:
        conn.close()


def handleBigramPass(indexpath, workdir):
    print(indexpath, workdir, 'bigram pass')
    length = 2

    sep = config.getWordSep()

    filename = config.getNgramFileName(length)
    filepath = workdir + os.sep + filename

    #begin processing
    conn = sqlite3.connect(filepath)
    cur = conn.cursor()

    cur.execute(DELETE_BIGRAM_DML)
    rows = cur.execute(SELECT_ALL_NGRAM_DML).fetchall()
    for row in rows:
        (words_str, freq) = row

        words = words_str.strip(sep).split(sep, 1)
        assert len(words) == length

        (prefix, postfix) = words

        cur.execute(INSERT_BIGRAM_DML, (prefix, postfix, freq))
        #print(prefix, postfix, freq)

    conn.commit()

    if conn:
        conn.close()


def handleOneIndex(indexpath, subdir, indexname, fast):
    print(indexpath, subdir, indexname)

    indexstatuspath = indexpath + config.getStatusPostfix()
    indexstatus = utils.load_status(indexstatuspath)
    if not utils.check_epoch(indexstatus, 'PartialWord'):
        raise utils.EpochError('Please do partial word first.\n')
    if utils.check_epoch(indexstatus, 'PopulateBigram'):
        return

    workdir = config.getWordRecognizerDir() + os.sep + \
        subdir + os.sep + indexname
    print(workdir)

    createBigramSqlite(indexpath, workdir)
    handleBigramPass(indexpath, workdir)

    #sign epoch
    utils.sign_epoch(indexstatus, 'PopulateBigram')
    utils.store_status(indexstatuspath, indexstatus)


def walkThroughIndex(path):
    for root, dirs, files in os.walk(path, topdown=True, onerror=handleError):
        for onefile in files:
            filepath = os.path.join(root, onefile)
            indexpostfix = config.getIndexPostfix()
            if onefile.endswith(indexpostfix):
                subdir = os.path.relpath(root, path)
                indexname = onefile[:-len(indexpostfix)]
                handleOneIndex(filepath, subdir, indexname)
            elif onefile.endswith(config.getStatusPostfix()):
                pass
            else:
                print('Unexpected file:' + filepath)
