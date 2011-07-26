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


#Note: all file passed here should be trained.
def generateOneText(infile, modelfile, reportfile):
    infilestatuspath = infile + config.getStatusPostfix()
    infilestatus = utils.load_status(infilestatuspath)
    if not utils.check_epoch(infilestatus, 'Segment'):
        raise utils.EpochError('Please segment first.\n')
    if utils.check_epoch(infilestatus, 'Generate'):
        return

    #begin processing
    cmdline = ['./gen_k_mixture_model', '--maximum-occurs-allowed', \
                   config.getMaximumOccursAllowed(), \
                   '--maximum-increase-rates-allowed', \
                   config.getMaximumIncreaseRatesAllowed(), \
                   '--k-mixture-model-file', \
                   modelfile, infile + \
                   config.getSegmentPostfix()]
    subprocess = Popen(cmdline, shell=False, stderr=PIPE, \
                           close_fds=True)

    lines = subprocess.stderr.readlines()
    if lines:
        print('found error report')
        with open(reportfile, 'ab') as f:
            f.writelines(lines)
        f.close()

    os.waitpid(subprocess.pid, 0)
    #end processing

    utils.sign_epoch(infilestatus, 'Generate')
    utils.store_status(infilestatuspath, infilestatus)


#Note: should check the corpus file size, and skip the too small text file.
def handleOneIndex(indexpath, subdir, indexname):
    print(indexpath, subdir, indexname)

    indexstatuspath = indexpath + config.getStatusPostfix()
    indexstatus = utils.load_status(indexstatuspath)
    if not utils.check_epoch(indexstatus, 'Segment'):
        raise utils.EpochError('Please segment first.\n')
    if utils.check_epoch(indexstatus, 'Generate'):
        return

    #continue generating
    textnum, modelnum, aggmodelsize = 0, 0, 0
    if 'GenerateTextEnd' in indexstatus:
        textnum = indexstatus['GenerateTextEnd']
    if 'GenerateModelEnd' in indexstatus:
        modelnum = indexstatus['GenerateModelEnd']

    #begin processing
    indexfile = open(indexpath, 'r')
    for i, oneline in enumerate(indexfile.readlines()):
        #continue last generating
        if i < textnum:
            continue

        #remove trailing '\n'
        oneline = oneline.rstrip(os.linesep)
        (title, textpath) = oneline.split('#')
        infile = config.getTextDir() + textpath
        infilesize = utils.get_file_length(infile + config.getSegmentPostfix())
        if infilesize < config.getMinimumFileSize():
            print("Skipping " + title + '#' + textpath)
            continue
        aggmodelsize += infilesize
        modeldir = os.path.join(config.getModelDir(), subdir, indexname)
        os.makedirs(modeldir, exist_ok=True)
        modelfile = os.path.join(modeldir, \
                                 config.getCandidateModelName(modelnum))
        reportfile = modelfile + config.getReportPostfix()
        print("Proccessing " + title + '#' + textpath)
        generateOneText(infile, modelfile, reportfile)
        print("Processed " + title + '#' + textpath)
        if aggmodelsize > config.getCandidateModelSize():
            nexttextnum = i + 1
            #store model info in status file
            modelstatuspath = modelfile + config.getStatusPostfix()
            #create None status
            modelstatus = {}
            modelstatus['GenerateStart'] = textnum
            modelstatus['GenerateEnd'] = nexttextnum
            utils.sign_epoch(modelstatus, 'Generate')
            utils.store_status(modelstatuspath, modelstatus)

            #new model candidate
            aggmodelsize = 0
            textnum = nexttextnum
            modelnum += 1
            modeldir = os.path.join(config.getModelDir(), subdir, indexname)
            modelfile = os.path.join( \
                modeldir, config.getCandidateModelName(modelnum))
            reportfile = modelfile + config.getReportPostfix()
            if os.access(modelfile, os.F_OK):
                os.unlink(modelfile)
            if os.access(reportfile, os.F_OK):
                os.unlink(reportfile)
            #save current progress in status file
            indexstatus['GenerateTextEnd'] = nexttextnum
            indexstatus['GenerateModelEnd'] = modelnum
            utils.store_status(indexstatuspath, indexstatus)
            pass
    indexfile.close()
    #end processing

    utils.sign_epoch(indexstatus, 'Generate')
    utils.store_status(indexstatuspath, indexstatus)


def walkThroughIndex(path):
    for root, dirs, files in os.walk(path, topdown=True, onerror=handleError):
        for onefile in files:
            filepath = os.path.join(root, onefile)
            indexpostfix = config.getIndexPostfix()
            if onefile.endswith(indexpostfix):
                subdir = os.path.relpath(root, path)
                indexname = onefile[:-len(indexpostfix)]
                handleOneIndex(filepath, subdir, indexname)
            elif onefile.endswith(config.getStatusPostfix()):
                pass
            else:
                print('Unexpected file:' + filepath)

if __name__ == '__main__':
    parser = ArgumentParser(description='Generate model candidates.')
    parser.add_argument('--indexdir', action='store', \
                            help='index directory', \
                            default=os.path.join(config.getTextDir(), 'index'))

    args = parser.parse_args()
    print(args)
    walkThroughIndex(args.indexdir)
    print('done')
