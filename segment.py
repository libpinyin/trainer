#!/usr/bin/python3
import os
import os.path
from subprocess import Popen, PIPE


def handleError(error):
    sys.exit(error)

def segmentOneText(infile, outfile):
    pass

def handleOneIndex(indexpath):
    indexfile = open(indexpath, 'r')
    for oneline in indexfile.readlines():
        (title, textpath) = oneline.split('#')
        infile = config.getTextDir() + textpath
        outfile = config.getTextDir() + textpath + config.getSegmentPostfix()
        print("Processing " + title)
        segmentOneText(infile, outfile)
        print("Processed "+ title)
    indexfile.close()

def walkThroughIndex(path):
    for root, dirs, files in os.walk(path, topdown=True, onerror=handleError):
        for onefile in files:
            filepath = os.path.join(root, onefile)
            if onefile.endswith(config.getIndexPostfix()):
                handleOneIndex(filepath)
            else:
                print('Unexpected file:' + filepath)


if __name__ == '__main__':
    pass
