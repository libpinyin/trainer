#!/usr/bin/python3
import os
import os.path
import sqlite3
from argparse import ArgumentParser
import utils
from myconfig import MyConfig
from dirwalk import walkIndex


CREATE_NGRAM_DDL = '''
CREATE TABLE ngram (
      words TEXT NOT NULL,
      freq INTEGER NOT NULL
      );
'''

CREATE_NGRAM_INDEX_DDL = '''
CREATE UNIQUE INDEX ngram_index on ngram(words);
'''


config = MyConfig()

#maximum combine number
N = config.getMaximumCombineNumber()

#change cwd to the word recognizer directory
words_dir = config.getWordRecognizerDir()
os.makedirs(words_dir, exist_ok=True)
os.chdir(words_dir)
#chdir done


def createSqliteDatabases(onedir):
    print(onedir)

    #create databases
    for i in range(1, N + 1):
        filename = config.getNgramFileName(i)
        filepath = onedir + os.sep + filename
        print(filepath)

        #create database
        if os.access(filepath, os.F_OK):
            os.unlink(filepath)

        conn = sqlite3.connect(filepath)

        cur = conn.cursor()

        cur.execute(CREATE_NGRAM_DDL)
        cur.execute(CREATE_NGRAM_INDEX_DDL)

        conn.commit()

        if conn:
            conn.close()


def handleOneIndex(indexpath, subdir, indexname):
    print(indexpath, subdir, indexname)

    indexstatuspath = indexpath + config.getStatusPostfix()
    indexstatus = utils.load_status(indexstatuspath)
    if not utils.check_epoch(indexstatus, 'Segment'):
        raise utils.EpochError('Please segment first.\n')
    if utils.check_epoch(indexstatus, 'Prepare'):
        return

    #create directory
    onedir = config.getWordRecognizerDir() + os.sep + \
        subdir + os.sep + indexname
    os.makedirs(onedir, exist_ok=True)

    #create sqlite databases
    createSqliteDatabases(onedir)

    #sign epoch
    utils.sign_epoch(indexstatus, 'Prepare')
    utils.store_status(indexstatuspath, indexstatus)


if __name__ == '__main__':
    parser = ArgumentParser(description='Prepare word recognizer.')
    parser.add_argument('--indexdir', action='store', \
                            help='index directory', \
                            default=os.path.join(config.getTextDir(), 'index'))

    args = parser.parse_args()
    print(args)
    walkIndex(handleOneIndex, args.indexdir)
    print('done')
