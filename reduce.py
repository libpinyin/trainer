#!/usr/bin/python3
import os
import os.path
import sys
from argparse import ArgumentParser
from myconfig import MyConfig
from utils import read_file


config = MyConfig()


def handleError(error):
    sys.exit(error)


def mergeSubIndex(output, path):
    for root, dirs, files in os.walk(path, topdown=True, onerror=handleError):
        for onefile in files:
            filepath = os.path.join(root, onefile)
            if onefile.endswith(config.getIndexPostfix()):
                data = read_file(filepath)
                output.writelines([data])
            else:
                print('Unexpected file:' + filepath)


def iterateSubDirectory(oldroot, newroot, level):
    #Merge the index in oldroot
    if level <= 0:
        newindex = newroot + config.getIndexPostfix()
        os.makedirs(os.path.dirname(newindex), exist_ok=True)
        newindexfile = open(newindex, 'a')
        mergeSubIndex(newindexfile, oldroot)
        newindexfile.close()
        return
    #Recursive into the sub directories
    for onedir in os.listdir(oldroot):
        olddir = os.path.join(oldroot, onedir)
        newdir = os.path.join(newroot, onedir)

        if not os.path.isdir(olddir):
            sys.exit('Un-expected file:' + olddir)
        else:
            iterateSubDirectory(olddir, newdir, level - 1)


if __name__ == '__main__':
    parser = ArgumentParser(description='Reduce the categories.')
    parser.add_argument('--level', action='store', nargs=1, default=2)
    parser.add_argument('origdir', action='store')
    parser.add_argument('destdir', action='store')

    args = parser.parse_args()
    iterateSubDirectory(args.origdir, args.destdir, int(args.level[0]))
    print('done')
