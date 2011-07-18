#!/usr/bin/python3
import os
import os.path
from argparse import ArgumentParser
from subprocess import Popen, PIPE
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
    cmdline = './ngseg <"' + infile + '" 2>"' + reportfile + '"'
    subprocess = Popen(cmdline, shell=True, stdout=PIPE, \
                           close_fds=True)

    with open(outfile, 'wb') as f:
        f.writelines(subprocess.stdout.readlines())
    f.close()

    os.waitpid(subprocess.pid, 0)

def handleOneIndex(indexpath):
    indexfile = open(indexpath, 'r')
    for oneline in indexfile.readlines():
        (title, textpath) = oneline.split('#')
        #remove tailing '\n'
        textpath = textpath.rstrip(os.linesep)
        infile = config.getTextDir() + textpath
        outfile = config.getTextDir() + textpath + config.getSegmentPostfix()
        reportfile = config.getTextDir() + textpath + \
            config.getSegmentReportPostfix()
        print("Processing " + title + '#' + textpath)
        segmentOneText(infile, outfile, reportfile)
        print("Processed "+ title + '#' + textpath)
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
    parser = ArgumentParser(description='Segment all raw corpus documents.')
    parser.add_argument('indexdir', action='store', \
                            help='index directory')

    args = parser.parse_args()
    walkThroughIndex(args.indexdir)
    print('done')


