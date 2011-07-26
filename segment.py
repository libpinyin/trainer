#!/usr/bin/python3
import os
import os.path
import sys
from argparse import ArgumentParser
from subprocess import Popen, PIPE
import utils
from myconfig import MyConfig


config = MyConfig()

#change cwd to the libpinyin utils/segment directory
libpinyin_dir = config.getToolsDir()
libpinyin_sub_dir = os.path.join(libpinyin_dir, 'utils', 'segment')
os.chdir(libpinyin_sub_dir)
#chdir done


def handleError(error):
    sys.exit(error)


def segmentOneText(infile, outfile, reportfile):
    infilestatuspath = infile + config.getStatusPostfix()
    infilestatus = utils.load_status(infilestatuspath)
    if utils.check_epoch(infilestatus, 'Segment'):
        return

    #begin processing
    cmdline = './ngseg >"' + outfile + '"'
    subprocess = Popen(cmdline, shell=True, stdin=PIPE, stderr=PIPE, \
                           close_fds=True)

    with open(infile, 'rb') as f:
        subprocess.stdin.writelines(f.readlines())
    subprocess.stdin.close()
    f.close()

    lines = subprocess.stderr.readlines()
    if lines:
        print('found error report')
        with open(reportfile, 'wb') as f:
            f.writelines(lines)
        f.close()

    os.waitpid(subprocess.pid, 0)
    #end processing

    utils.sign_epoch(infilestatus, 'Segment')
    utils.store_status(infilestatuspath, infilestatus)


def handleOneIndex(indexpath):
    indexstatuspath = indexpath + config.getStatusPostfix()
    indexstatus = utils.load_status(indexstatuspath)
    if utils.check_epoch(indexstatus, 'Segment'):
        return

    #begin processing
    indexfile = open(indexpath, 'r')
    for oneline in indexfile.readlines():
        #remove tailing '\n'
        oneline = oneline.rstrip(os.linesep)
        (title, textpath) = oneline.split('#')
        infile = config.getTextDir() + textpath
        outfile = config.getTextDir() + textpath + config.getSegmentPostfix()
        reportfile = config.getTextDir() + textpath + \
            config.getSegmentReportPostfix()
        print("Processing " + title + '#' + textpath)
        segmentOneText(infile, outfile, reportfile)
        print("Processed " + title + '#' + textpath)
    indexfile.close()
    #end processing

    utils.sign_epoch(indexstatus, 'Segment')
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
    parser = ArgumentParser(description='Segment all raw corpus documents.')
    parser.add_argument('--indexdir', action='store', \
                            help='index directory', \
                            default=os.path.join(config.getTextDir(), 'index'))

    args = parser.parse_args()
    print(args)
    walkThroughIndex(args.indexdir)
    print('done')
