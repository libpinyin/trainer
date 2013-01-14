#!/usr/bin/python3
import os
import os.path
import sqlite3
from argparse import ArgumentParser
import utils
from myconfig import MyConfig


INSERT_NGRAM_DML = '''
INSERT INTO ngram(words, freq) VALUES(?, 1);
'''

UPDATE_NGRAM_DML = '''
UPDATE ngram SET freq = freq + 1 WHERE words = ?;
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

#maximum combine number
N = config.getMaximumCombineNumber()

#change cwd to the word recognizer directory
words_dir = config.getWordRecognizerDir()
os.makedirs(words_dir, exist_ok=True)
os.chdir(words_dir)
#chdir done


def handleError(error):
    sys.exit(error)


def handleOneDocument(infile, conn, length):
    print(infile, length)

    infilestatuspath = infile + config.getStatusPostfix()
    infilestatus = utils.load_status(infilestatuspath)
    if not utils.check_epoch(infilestatus, 'Segment'):
        raise utils.EpochError('Please segment first.\n')
    if utils.check_epoch(infilestatus, 'Populate'):
        return False

    sep = config.getWordSep()

    #train
    docfile = open(infile + config.getSegmentPostfix(), 'r')
    words = []

    cur = conn.cursor()

    for oneline in docfile.readlines():
        oneline = oneline.rstrip(os.linesep)

        if len(oneline) == 0:
            continue

        (token, word) = oneline.split(" ", 1)
        token = int(token)

        if 0 == token:
            words = []
        else:
            words.append(word)

        if len(words) < length:
            continue

        if len(words) > length:
            words.pop(0)

        assert len(words) == length

        #do sqlite training
        words_str = sep + sep.join(words) + sep
        #print(words_str)

        rowcount = cur.execute(UPDATE_NGRAM_DML, (words_str,)).rowcount
        #print(rowcount)
        if 0 == rowcount:
            cur.execute(INSERT_NGRAM_DML, (words_str,))

    docfile.close()

    #sign epoch only after last pass
    if N == length:
        utils.sign_epoch(infilestatus, 'Populate')
        utils.store_status(infilestatuspath, infilestatus)

    return True

def handleOnePass(indexpath, workdir, length):
    print(indexpath, workdir, length)

    filename = config.getNgramFileName(length)
    filepath = workdir + os.sep + filename

    conn = sqlite3.connect(filepath)

    #begin processing
    indexfile = open(indexpath, 'r')

    for oneline in indexfile.readlines():
        oneline = oneline.rstrip(os.linesep)
        (title, textpath) = oneline.split('#')
        infile = config.getTextDir() + textpath
        infilesize = utils.get_file_length(infile + config.getSegmentPostfix())
        if infilesize < config.getMinimumFileSize():
            print("Skipping " + title + '#' + textpath)
            continue

        #process one document
        handleOneDocument(infile, conn, length)

    indexfile.close()

    conn.commit()

    if conn:
        conn.close()

def handleBigramPass(indexpath, workdir):
    print(indexpath, workdir, 'bigram')
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
    if not utils.check_epoch(indexstatus, 'Prepare'):
        raise utils.EpochError('Please prepare first.\n')
    if utils.check_epoch(indexstatus, 'Populate'):
        return

    workdir = config.getWordRecognizerDir() + os.sep + \
        subdir + os.sep + indexname
    print(workdir)

    shmdir = config.getInMemoryFileSystem()

    for i in range(1, N + 1):
        if fast:
            #copy file
            filename = config.getNgramFileName(i)
            filepath = workdir + os.sep + filename
            shmfilepath = shmdir + os.sep + filename
            utils.copyfile(filepath, shmfilepath)
            handleOnePass(indexpath, shmdir, i)
            utils.copyfile(shmfilepath, filepath)
            os.unlink(shmfilepath)
        else:
            handleOnePass(indexpath, workdir, i)

    handleBigramPass(indexpath, workdir)

    #sign epoch
    utils.sign_epoch(indexstatus, 'Populate')
    utils.store_status(indexstatuspath, indexstatus)
    


def walkThroughIndex(path, fast):
    for root, dirs, files in os.walk(path, topdown=True, onerror=handleError):
        for onefile in files:
            filepath = os.path.join(root, onefile)
            indexpostfix = config.getIndexPostfix()
            if onefile.endswith(indexpostfix):
                subdir = os.path.relpath(root, path)
                indexname = onefile[:-len(indexpostfix)]
                handleOneIndex(filepath, subdir, indexname, fast)
            elif onefile.endswith(config.getStatusPostfix()):
                pass
            else:
                print('Unexpected file:' + filepath)


if __name__ == '__main__':
    parser = ArgumentParser(description='Populate n-gram.')
    parser.add_argument('--indexdir', action='store', \
                            help='index directory', \
                            default=os.path.join(config.getTextDir(), 'index'))

    parser.add_argument('--fast', action='store_const', \
                            help='Use /dev/shm to speed up populate', \
                            const=True, default=False)


    args = parser.parse_args()
    print(args)
    walkThroughIndex(args.indexdir, args.fast)
    print('done')
