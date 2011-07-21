#!/usr/bin/python3
from myconfig import MyConfig


config = MyConfig()

#change cwd to the libpinyin utils/training directory
libpinyin_dir = config.getToolsDir()
libpinyin_sub_dir = os.path.join(libpinyin_dir, 'utils', 'training')
os.chdir(libpinyin_sub_dir)
#chdir done

def handleError(error):
    sys.exit(error)


#Note: all file passed here should be trained.
def generateOneText(infile, modelfile):
    pass

#Note: should check the corpus file size, and skip the too small text file.
def handleOneIndex(indexpath):
    pass

def walkThroughIndex(path):
    pass

if __name__ == '__main__':
    pass
