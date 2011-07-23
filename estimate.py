#!/usr/bin/python3
import os
import os.path
import sys
from subprocess import Popen, PIPE
from argparse import ArgumentParser
from operator import itemgetter
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
                subpath = os.path.relpath(filepath, path)
                print("Processing " + subpath)
                handleOneModel(filepath)
                print("Processed " + subpath)
            elif onefile.endswith(config.getStatusPostfix()):
                pass
            elif onefile.endswith(config.getIndexPostfix()):
                pass
            else:
                print('Unexpected file:' + filepath)

def gatherModels(path, indexname):
    indexfilestatuspath = indexname + config.getStatusPostfix()
    indexfilestatus = utils.load_status(indexfilestatuspath)
    if utils.check_epoch(indexfilestatuspath, 'Estimate'):
        return

    #begin processing
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
    #end processing

    utils.sign_epoch(indexfilestatus, 'Estimate')
    utils.store_status(indexfilestatuspath, indexfilestatus)

def sortModels(indexname, sortedindexname):
    sortedindexfilestatuspath = sortedindexname + config.getStatusPostfix()
    sortedindexfilestatus = utils.load_status(sortedindexfilestatuspath)
    if utils.check_epoch(sortedindexfilestatus, 'Estimate'):
        return        

    #begin processing
    records = []
    indexfile = open(indexname, 'r')
    for line in indexfile.readlines():
        #remove the trailing '\n'
        line = line.rstrip(os.linesep)
        (subdir, modelname, score) = line.split('#', 2)
        score = float(score)
        records.append((subdir, modelname, score))
    indexfile.close()

    records.sort(key=itemgetter(2), reverse=True)

    sortedindexfile = open(sortedindexname, 'w')
    for record in records:
        (subdir, modelname, score) = record
        line = subdir + '#' + modelname + '#' + score
        sortedindexfile.writelines([line])
    sortedindexfile.close()
    #end processing

    utils.sign_epoch(sortedindexfilestatus, 'Estimate')
    utils.store_status(sortedindexfilestatuspath, sortedindexfilestatus)

if __name__ == '__main__':
    parser = ArgumentParser(description='Estimate model candidates.')
    parser.add_argument('--modeldir', action='store', \
                            help='model directory', \
                            default=config.getModelDir())

    args = parser.parse_args()
    print(args)
    print("estimating")
    walkThroughModels(args.modeldir)
    print("gathering")
    indexname = os.path.join(args.modeldir, config.getEstimateIndex())
    gatherModels(args.modeldir, indexname)
    print("sorting")
    sortedindexname = os.path.join(args.modeldir, \
                                       config.getSortedEstimateIndex())
    sortModels(indexname, sortedindexname)
    print("done")
