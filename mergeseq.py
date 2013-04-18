#!/usr/bin/python3
import os
import os.path
import sys
from argparse import ArgumentParser
from subprocess import Popen, PIPE
import utils
from myconfig import MyConfig


config = MyConfig()

#change cwd to the libpinyin data directory
libpinyin_dir = config.getToolsDir()
libpinyin_sub_dir = os.path.join(libpinyin_dir, 'data')
os.chdir(libpinyin_sub_dir)
#chdir done


def handleError(error):
    sys.exit(error)


def mergeOneText(infile, outfile, reportfile):
    infilestatuspath = infile + config.getStatusPostfix()
    infilestatus = utils.load_status(infilestatuspath)
    if not utils.check_epoch(infilestatus, 'Segment'):
        raise utils.EpochError('Please segment first.\n')
    if utils.check_epoch(infilestatus, 'MergeSequence'):
        return

    infile = infile + config.getSegmentPostfix()

    #begin processing
    cmdline = ['../utils/segment/mergeseq', \
                   '-o', outfile, infile]

    subprocess = Popen(cmdline, shell=False, stderr=PIPE, \
                           close_fds=True)

    lines = subprocess.stderr.readlines()
    if lines:
        print('found error report')
        with open(reportfile, 'wb') as f:
            f.writelines(lines)

    os.waitpid(subprocess.pid, 0)
    #end processing

    utils.sign_epoch(infilestatus, 'MergeSequence')
    utils.store_status(infilestatuspath, infilestatus)


def handleOneIndex(indexpath):
    indexstatuspath = indexpath + config.getStatusPostfix()
    indexstatus = utils.load_status(indexstatuspath)
    if not utils.check_epoch(indexstatus, 'Segment'):
        raise utils.EpochError('Please segment first.\n')
    if utils.check_epoch(indexstatus, 'MergeSequence'):
        return

    #begin processing
    indexfile = open(indexpath, 'r')
    for oneline in indexfile.readlines():
        #remove tailing '\n'
        oneline = oneline.rstrip(os.linesep)
        (title, textpath) = oneline.split('#')

        infile = config.getTextDir() + textpath
        outfile = config.getTextDir() + textpath + config.getMergedPostfix()
        reportfile = config.getTextDir() + textpath + \
            config.getMergedReportPostfix()

        print("Processing " + title + '#' + textpath)
        mergeOneText(infile, outfile, reportfile)
        print("Processed " + title + '#' + textpath)

    indexfile.close()
    #end processing

    utils.sign_epoch(indexstatus, 'MergeSequence')
    utils.store_status(indexstatuspath, indexstatus)


def walkThroughIndex(path):
    for root, dirs, files in os.walk(path, topdown=True, onerror=handleError):
        for onefile in files:
            filepath = os.path.join(root, onefile)
            if onefile.endswith(config.getIndexPostfix()):
                handleOneIndex(filepath)
            elif onefile.endswith(config.getStatusPostfix()):
                pass
            else:
                print('Unexpected file:' + filepath)

if __name__ == '__main__':
    parser = ArgumentParser(description='Merge all corpus segmented documents.')
    parser.add_argument('--indexdir', action='store', \
                            help='index directory', \
                            default=config.getTextIndexDir())

    args = parser.parse_args()
    print(args)
    walkThroughIndex(args.indexdir)
    print('done')


