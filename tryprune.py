#!/usr/bin/python3
import os
import sys
from subprocess import Popen, PIPE
from argparse import ArgumentParser
from myconfig import MyConfig


config = MyConfig()

#change cwd to the libpinyin utils/training directory
libpinyin_dir = config.getToolsDir()
libpinyin_sub_dir = os.path.join(libpinyin_dir, 'utils', 'training')
os.chdir(libpinyin_sub_dir)
#chdir done

def validateModel(modelfile):
    #begin processing
    cmdline = ['./validate_k_mixture_model', \
                   modelfile]

    subprocess = Popen(cmdline, shell=False, close_fds=True)
    #check os.waitpid doc
    (pid, status) = os.waitpid(subprocess.pid, 0)
    if status != 0:
        sys.exit('Corrupted model found when validating:' + modelfile)
    #end processing

def exportModel(modelfile, textmodel):
    #begin processing
    cmdline = ['./export_k_mixture_model', \
                   '--k-mixture-model-file', \
                   modelfile]

    subprocess = Popen(cmdline, shell=False, stdout=PIPE, \
                           close_fds=True)

    with open(textmodel, 'wb') as f:
        f.writelines(subprocess.stdout.readlines())
    f.close()

    #check os.waitpid doc
    (pid, status) = os.waitpid(subprocess.pid, 0)
    if status != 0:
        sys.exit('Corrupted model found when exporting:' + modelfile)
    #end processing

def mergeOneModel(mergedmodel, onemodel):
    #begin processing
    cmdline = ['./merge_k_mixture_model', \
                   '--result-file', \
                   mergedmodel, \
                   onemodel]

    subprocess = Popen(cmdline, shell=False, close_fds=True)
    #check os.waitpid doc
    (pid, status) = os.waitpid(subprocess.pid, 0)
    if status != 0:
        sys.exit('Corrupted model found when merging:' + onemodel)
    #end processing

def mergeSomeModels(indexfile, mergenum):
    pass

def pruneModel(modelfile, k, CDF):
    #begin processing
    cmdline = ['./prune_k_mixture_model', \
               '-k', k, '--CDF', CDF,
               modelfile]

    subprocess = Popen(cmdline, shell=False, close_fds=True)
    #check os.waitpid doc
    (pid, status) = os.waitpid(subprocess.pid, 0)
    if (status != 0):
        sys.exit('Corrupted model found when pruning:' + modelfile)
    #end processing

if __name__ == '__main__':
    parser = ArgumentParser(description='Try prune models.')
    parser.add_argument('--modeldir', action='store', \
                            help='model directory', \
                            default=config.getModelDir())

    parser.add_argument('--mergenumber', action='store', \
                            help='number of documents to be merged', \
                            default='10')

    parser.add_argument('-k', action='store', \
                            help='k parameter of k mixture model prune', \
                            default='3')

    parser.add_argument('--CDF', action='store', \
                            help='CDF parameter of k mixture model prune', \
                            default='0.99')

    parser.add_argument('tryname', action='store', \
                            help='the storage directory')

    args = parser.parse_args()
    print(args)
