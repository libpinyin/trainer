#!/usr/bin/python3
import os
import os.path
import shutil
import sys
from subprocess import Popen, PIPE
from argparse import ArgumentParser
from myconfig import MyConfig
import utils


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

    (pid, status) = os.waitpid(subprocess.pid, 0)
    if status != 0:
        sys.exit('Corrupted model found when exporting:' + modelfile)
    #end processing


def convertModel(kmm_model, inter_model):
    #begin processing
    cmdline = './k_mixture_model_to_interpolation <"' + kmm_model + '"'

    subprocess = Popen(cmdline, shell=True, \
                           stdout=PIPE, close_fds=True)

    with open(inter_model, 'wb') as f:
        f.writelines(subprocess.stdout.readlines())
    f.close()

    (pid, status) = os.waitpid(subprocess.pid, 0)
    if status != 0:
        sys.exit('Corrupted model found when converting:' + kmm_model)
    #end processing


def mergeOneModel(mergedmodel, onemodel, score):
    #validate first
    validateModel(onemodel)

    onemodelstatuspath = onemodel + config.getStatusPostfix()
    onemodelstatus = utils.load_status(onemodelstatuspath)
    if not utils.check_epoch(onemodelstatus, 'Estimate'):
        raise utils.Epoch('Please estimate first.\n')
    if score != onemodelstatus['EstimateScore']:
        raise AssertionError('estimate scores mis-match.\n')

    #begin processing
    cmdline = ['./merge_k_mixture_model', \
                   '--result-file', \
                   mergedmodel, \
                   onemodel]

    subprocess = Popen(cmdline, shell=False, close_fds=True)

    (pid, status) = os.waitpid(subprocess.pid, 0)
    if status != 0:
        sys.exit('Corrupted model found when merging:' + onemodel)
    #end processing


def mergeSomeModels(mergedmodel, sortedindexname, mergenum):
    last_score = 1.
    #begin processing
    indexfile = open(sortedindexname, 'r')
    for i in range(mergenum):
        line = indexfile.readline()
        if not line:
            raise AssertionError('No more models.\n')
        line = line.rstrip(os.linesep)
        (subdir, modelname, score) = line.split('#', 2)
        score = float(score)
        if score > last_score:
            raise AssertionError('scores must be descending.\n')

        onemodel = os.path.join(config.getModelDir(), subdir, modelname)
        mergeOneModel(mergedmodel, onemodel, score)
        last_score = score
    indexfile.close()
    #end processing

    #validate merged model
    validateModel(mergedmodel)


def pruneModel(prunedmodel, k, CDF):
    #begin processing
    cmdline = ['./prune_k_mixture_model', \
               '-k', str(k), '--CDF', str(CDF),
               prunedmodel]

    subprocess = Popen(cmdline, shell=False, close_fds=True)

    (pid, status) = os.waitpid(subprocess.pid, 0)
    if (status != 0):
        sys.exit('Corrupted model found when pruning:' + modelfile)
    #end processing

    #validate pruned model
    validateModel(prunedmodel)

if __name__ == '__main__':
    parser = ArgumentParser(description='Try prune models.')
    parser.add_argument('--modeldir', action='store', \
                            help='model directory', \
                            default=config.getModelDir())

    parser.add_argument('--merge', action='store', \
                            help='number of model candidates to be merged', \
                            default=10, type=int)

    parser.add_argument('-k', action='store', \
                            help='k parameter of k mixture model prune', \
                            default=3, type=int)

    parser.add_argument('--CDF', action='store', \
                            help='CDF parameter of k mixture model prune', \
                            default=0.99, type=float)

    parser.add_argument('tryname', action='store', \
                            help='the storage directory')

    args = parser.parse_args()
    print(args)
    tryname = 'try' + args.tryname

    trydir = os.path.join(config.getFinalModelDir(), tryname)

    #check try<name> directory
    if os.access(trydir, os.F_OK):
        sys.exit(tryname + ' exists.')

    os.makedirs(trydir)
    cwdstatuspath = os.path.join(trydir, config.getFinalStatusFileName())
    cwdstatus = {}
    cwdstatus['PruneMergeNumber'] = args.merge
    cwdstatus['PruneK'] = args.k
    cwdstatus['PruneCDF'] = args.CDF
    utils.store_status(cwdstatuspath, cwdstatus)

    #merge model candidates
    print('merging')
    mergedmodel = os.path.join(trydir, 'merged.db')
    sortedindexname = os.path.join(args.modeldir, \
                                       config.getSortedEstimateIndex())
    mergeSomeModels(mergedmodel, sortedindexname, args.merge)

    #export textual format
    print('exporting')
    exportfile = os.path.join(trydir, 'kmm_merged.text')
    exportModel(mergedmodel, exportfile)

    #prune merged model
    print('pruning')
    prunedmodel = os.path.join(trydir, 'pruned.db')
    #backup merged model
    shutil.copyfile(mergedmodel, prunedmodel)
    pruneModel(prunedmodel, args.k, args.CDF)

    #export textual format
    print('exporting')
    exportfile = os.path.join(trydir, 'kmm_pruned.text')
    exportModel(prunedmodel, exportfile)

    #convert to interpolation
    print('converting')
    kmm_model = exportfile
    inter_model = os.path.join(trydir, config.getFinalModelFileName())
    convertModel(kmm_model, inter_model)

    modelsize = utils.get_file_length(inter_model)
    cwdstatus['PruneModelSize'] = modelsize
    utils.store_status(cwdstatuspath, cwdstatus)

    print('final model size:', modelsize)

    #sign status epoch
    utils.sign_epoch(cwdstatus, 'Prune')
    utils.store_status(cwdstatuspath, cwdstatus)
    print('done')
