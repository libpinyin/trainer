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

    filename = config.getBigramFileName()
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


def handleOneIndex(indexpath, subdir, indexname):
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


if __name__ == '__main__':
    parser = ArgumentParser(description='Populate bi-gram.')
    parser.add_argument('--indexdir', action='store', \
                            help='index directory', \
                            default=os.path.join(config.getTextDir(), 'index'))

    args = parser.parse_args()
    print(args)
    walkThroughIndex(args.indexdir)
    print('done')
