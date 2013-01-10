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

SELECT_ALL_DML = '''
SELECT words, freq FROM ngram;
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

        rowcount = cur.execute(UPDATE_NGRAM_DML, (words_str,)).rowcount
        #print(rowcount)
        if 0 == rowcount:
            cur.execute(INSERT_NGRAM_DML, (words_str,))

    docfile.close()

    #sign epoch
    #utils.sign_epoch(infilestatus, 'Populate')
    #utils.store_status(infilestatuspath, infilestatus)
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
    pass


def handleOneIndex(indexpath, subdir, indexname):
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

    for i in range(1, N + 1):
        handleOnePass(indexpath, workdir, i)

    handleBigramPass(indexpath, workdir)

    #sign epoch
    #utils.sign_epoch(indexstatus, 'Populate')
    #utils.store_status(indexstatuspath, indexstatus)
    


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
    parser = ArgumentParser(description='Populate n-gram.')
    parser.add_argument('--indexdir', action='store', \
                            help='index directory', \
                            default=os.path.join(config.getTextDir(), 'index'))

    args = parser.parse_args()
    print(args)
    walkThroughIndex(args.indexdir)
    print('done')
