#!/usr/bin/python3
import os
import os.path
from argparse import ArgumentParser
import utils
from myconfig import MyConfig
from dirwalk import walkIndex

config = MyConfig()

#change cwd to the generate punctuation directory
puncts_dir = config.getGeneratePunctuationDir()
os.path.exists(puncts_dir) or os.makedirs(puncts_dir)
os.chdir(puncts_dir)
#chdir done

# The order is important
Punct_Search = ['……', '…', '，', '。', '；', '？', '！', '：', '“', '”', '、']

############################################################
#                  Handle File                             #
############################################################

def handleOneText(infile, punct_pairs):
    global Punct_Search
    print(infile)

    sep = config.getWordSep()

    #train
    docfile = open(infile + config.getSegmentPostfix(), 'r')

    (prev_token, prev_str) = (0, '')
    (cur_token, cur_str) = (0, '')
    for oneline in docfile.readlines():
        oneline = oneline.rstrip(os.linesep)

        if len(oneline) == 0:
            continue

        (cur_token, cur_str) = oneline.split(" ", 1)
        cur_token = int(cur_token)

        if prev_token == 0:
            (prev_token, prev_str) = (cur_token, cur_str)
            continue

        #search the punct here
        cur_punct = ''
        if cur_token == 0:
            for punct in Punct_Search:
                if cur_str.startswith(punct):
                    cur_punct = punct
                    break

        if cur_punct == '':
            (prev_token, prev_str) = (cur_token, cur_str)
            continue

        #save the punct
        if (prev_token, prev_str) in punct_pairs:
            puncts = punct_pairs[(prev_token, prev_str)]
            for punct in puncts:
                if cur_punct == punct[0]:
                    punct[1] += 1
                    cur_punct = ''
                    #print(punct[0], punct[1])
                    break
            if cur_punct != '':
                puncts.append([cur_punct, 1])
        else:
            puncts = []
            puncts.append([cur_punct, 1])
            punct_pairs[(prev_token, prev_str)] = puncts

        (prev_token, prev_str) = (cur_token, cur_str)

    docfile.close()

def prunePunctPairFromOneIndex(workdir, threshold):
    punct_pairs = {}
    #load the punct pairs from text files
    punctfile = os.path.join(workdir, \
                             config.getPunctuationPerIndexFileName())
    with open(punctfile, 'r') as f:
        punct_pairs = eval(f.read())

    #prune the punct pairs below threshold
    newpunctpairs = {}
    for key, puncts in punct_pairs.items():
        (token, word) = key
        newpuncts = []
        for punct, freq in puncts:
            if freq < threshold:
                continue
            newpuncts.append([punct, freq])
        if len(newpuncts) > 0:
            newpunctpairs[key] = newpuncts

    #save the punct pairs to text files
    punctfile = os.path.join(workdir, \
                             config.getPunctuationPruneIndexFileName())
    with open(punctfile, 'w') as f:
        f.write(repr(newpunctpairs))


############################################################
#                  Handle Index                            #
############################################################

def loadPunctPairFromOneIndex(indexpath, workdir):
    punct_pairs = {}
    #begin processing
    indexfile = open(indexpath, 'r')
    for i, oneline in enumerate(indexfile.readlines()):
        #remove trailing '\n'
        oneline = oneline.rstrip(os.linesep)
        (title, textpath) = oneline.split('#')
        infile = config.getTextDir() + textpath
        infilesize = utils.get_file_length(infile + config.getSegmentPostfix())
        if infilesize < config.getMinimumFileSize():
            print("Skipping " + title + '#' + textpath)
            continue

        print("Proccessing " + title + '#' + textpath)
        handleOneText(infile, punct_pairs)
        print("Processed " + title + '#' + textpath)

    indexfile.close()
    #end processing

    #save the punct pairs to text files
    punctfile = os.path.join(workdir, \
                             config.getPunctuationPerIndexFileName())
    with open(punctfile, 'w') as f:
        f.write(repr(punct_pairs))


def handleOneIndex(indexpath, subdir, indexname):
    print(indexpath, subdir, indexname)

    indexstatuspath = indexpath + config.getStatusPostfix()
    indexstatus = utils.load_status(indexstatuspath)
    if not utils.check_epoch(indexstatus, 'Segment'):
        raise utils.EpochError('Please segment first.\n')
    if utils.check_epoch(indexstatus, 'Punctuation'):
        return

    workdir = config.getGeneratePunctuationDir() + os.sep + \
        subdir + os.sep + indexname
    print(workdir)

    # Iterate the files in this index
    os.path.exists(workdir) or os.makedirs(workdir)

    # Load all word and punctuation pair in this index
    loadPunctPairFromOneIndex(indexpath, workdir)

    # Prune the pair in the current index
    prunePunctPairFromOneIndex(workdir, \
                               config.getPunctuationPerIndexPruneThreshold())

    #sign epoch
    utils.sign_epoch(indexstatus, 'Punctuation')
    utils.store_status(indexstatuspath, indexstatus)


if __name__ == '__main__':
    parser = ArgumentParser(description='Generate punctuation.')
    parser.add_argument('--indexdir', action='store', \
                            help='index directory', \
                            default=config.getTextIndexDir())


    args = parser.parse_args()
    print(args)
    walkIndex(handleOneIndex, args.indexdir)
    # Merge the word and punctuation pairs in all the index

    # Prune the pairs in all the index

    # Export all the remaining pairs

    print('done')
