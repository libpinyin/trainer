#!/usr/bin/python3
import os
import os.path
import sys
from subprocess import Popen, PIPE
from argparse import ArgumentParser
import utils
from myconfig import MyConfig


config = MyConfig()

#change cwd to the libpinyin utils/training directory
libpinyin_dir = config.getToolsDir()
libpinyin_sub_dir = os.path.join(libpinyin_dir, 'utils', 'training')
os.chdir(libpinyin_sub_dir)
#chdir done

def handleError(error):
    sys.exit(error)

def handleOneModel(modelfile):
    modelfilestatuspath = modelfile + config.getStatusPostfix()
    modelfilestatus = utils.load_status(modelfilestatuspath)
    if not utils.check_epoch(modelfilestatus, 'Generate'):
        raise utils.EpochError('Please generate first.\n')
    if utils.check_epoch(modelfilestatus, 'Estimate'):
        return

    result_line_prefix = "average lambda:"
    avg_lambda = 0.

    #begin processing
    cmdline = ['./estimate_k_mixture_model', \
                   '--deleted-bigram-file', \
                   config.getEstimatesModel(), \
                   '--bigram-file', \
                   modelfile]

    subprocess = Popen(cmdline, shell=False, stdout=PIPE, \
                           close_fds= True)

    for line in subprocess.stdout.readlines():
        #remove trailing '\n'
        line = line.rstrip(os.linesep)
        if line.startswith(result_line_prefix):
            avg_lambda = float(line[len(result_line_prefix):])

    os.waitpid(subprocess.pid, 0)
    #end processing

    modelfilestatus['EstimateScore'] = avg_lambda
    utils.sign_epoch(modelfilestatus, 'Estimate')
    utils.store_status(modelfilestatuspath, modelfilestatus)

def walkThroughModels(path):
    for root, dirs, files in os.walk(path, topdown=True, onerror=handleError):
        for onefile in files:
            filepath = os.path.join(root, onefile)
            if onefile.endswith(config.getModelPostfix()):
                handleOneModel(filepath)
            elif onefile.endswith(config.getStatusPostfix()):
                pass
            elif onefile.endswith(config.getIndexPostfix()):
                pass
            else:
                print('Unexpected file:' + filepath)

def gatherModels(path, indexname):
    indexfile = open(indexname, "w")
    for root, dirs, files in os.walk(path, topdown=True, onerror=handleError):
        for onefile in files:
            filepath = os.path.join(root, onefile)
            if onefile.endswith(config.getModelPostfix()):
                #append one record to index file
                subdir = os.path.relpath(root, path)
                statusfilepath = filepath + config.getStatusPostfix()
                status = utils.load_status(statusfilepath)
                if not (utils.check_epoch(status, 'Estimate') and \
                        'EstimateScore' in status):
                    raise utils.EpochError('Unknown Error:\n' + \
                                               'Try re-run estimate.\n')
                avg_lambda = status['EstimateScore']
                line = subdir + '#' + onefile + '#' + avg_lambda
                indexfile.writelines([line])
                #record written
            elif onefile.endswith(config.getStatusPostfix()):
                pass
            elif onefile.endswith(config.getIndexPostfix()):
                pass
            else:
                print('Unexpected file:' + filepath)
    indexfile.close()

def sortModels(indexfilename, sortedindexfilename):
    pass

if __name__ == '__main__':
    pass
