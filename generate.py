#!/usr/bin/python3
import os
import os.path
import sys
from subprocess import Popen, PIPE
from argparse import ArgumentParser
import utils
from myconfig import MyConfig
from dirwalk import walkIndexFast

config = MyConfig()

#change cwd to the libpinyin data directory
libpinyin_dir = config.getToolsDir()
libpinyin_sub_dir = os.path.join(libpinyin_dir, 'data')
os.chdir(libpinyin_sub_dir)
#chdir done


#Note: all file passed here should be trained.
def generateOneText(infile, modelfile, reportfile):
    infilestatuspath = infile + config.getStatusPostfix()
    infilestatus = utils.load_status(infilestatuspath)
    if not utils.check_epoch(infilestatus, 'Segment'):
        raise utils.EpochError('Please segment first.\n')
    if utils.check_epoch(infilestatus, 'Generate'):
        return False

    #begin processing
    cmdline = ['../utils/training/gen_k_mixture_model', \
                   '--maximum-occurs-allowed', \
                   str(config.getMaximumOccursAllowed()), \
                   '--maximum-increase-rates-allowed', \
                   str(config.getMaximumIncreaseRatesAllowed()), \
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

    (pid, status) = os.waitpid(subprocess.pid, 0)
    if status != 0:
        sys.exit('gen_k_mixture_model encounters error.')
    #end processing

    utils.sign_epoch(infilestatus, 'Generate')
    utils.store_status(infilestatuspath, infilestatus)
    return True


#Note: should check the corpus file size, and skip the too small text file.
def handleOneIndex(indexpath, subdir, indexname, fast):
    inMemoryFile = "model.db"

    modeldir = os.path.join(config.getModelDir(), subdir, indexname)
    os.path.exists(modeldir) or os.makedirs(modeldir)


    def cleanupInMemoryFile():
        modelfile = os.path.join(config.getInMemoryFileSystem(), inMemoryFile)
        reportfile = modelfile + config.getReportPostfix()
        if os.access(modelfile, os.F_OK):
            os.unlink(modelfile)
        if os.access(reportfile, os.F_OK):
            os.unlink(reportfile)

    def copyoutInMemoryFile(modelfile):
        inmemoryfile = os.path.join\
            (config.getInMemoryFileSystem(), inMemoryFile)
        inmemoryreportfile = inmemoryfile + config.getReportPostfix()
        reportfile = modelfile + config.getReportPostfix()

        if os.access(inmemoryfile, os.F_OK):
            utils.copyfile(inmemoryfile, modelfile)
        if os.access(inmemoryreportfile, os.F_OK):
            utils.copyfile(inmemoryreportfile, reportfile)

    def cleanupFiles(modelnum):
        modeldir = os.path.join(config.getModelDir(), subdir, indexname)
        modelfile = os.path.join( \
            modeldir, config.getCandidateModelName(modelnum))
        reportfile = modelfile + config.getReportPostfix()
        if os.access(modelfile, os.F_OK):
            os.unlink(modelfile)
        if os.access(reportfile, os.F_OK):
            os.unlink(reportfile)

    def storeModelStatus(modelfile, textnum, nexttextnum):
        #store model info in status file
        modelstatuspath = modelfile + config.getStatusPostfix()
        #create None status
        modelstatus = {}
        modelstatus['GenerateStart'] = textnum
        modelstatus['GenerateEnd'] = nexttextnum
        utils.sign_epoch(modelstatus, 'Generate')
        utils.store_status(modelstatuspath, modelstatus)

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

    #clean up previous file
    if fast:
        cleanupInMemoryFile()

    cleanupFiles(modelnum)

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

        if fast:
            modelfile = os.path.join(config.getInMemoryFileSystem(), \
                                         inMemoryFile)
        else:
            modelfile = os.path.join(modeldir, \
                                         config.getCandidateModelName(modelnum))

        reportfile = modelfile + config.getReportPostfix()
        print("Proccessing " + title + '#' + textpath)
        if generateOneText(infile, modelfile, reportfile):
            aggmodelsize += infilesize
        print("Processed " + title + '#' + textpath)
        if aggmodelsize > config.getCandidateModelSize():
            #copy out in memory file
            if fast:
                modelfile = os.path.join\
                    (modeldir, config.getCandidateModelName(modelnum))
                copyoutInMemoryFile(modelfile)
                cleanupInMemoryFile()

            #the model file is in disk now
            nexttextnum = i + 1
            storeModelStatus(modelfile, textnum, nexttextnum)

            #new model candidate
            aggmodelsize = 0
            textnum = nexttextnum
            modelnum += 1

            #clean up next file
            cleanupFiles(modelnum)

            #save current progress in status file
            indexstatus['GenerateTextEnd'] = nexttextnum
            indexstatus['GenerateModelEnd'] = modelnum
            utils.store_status(indexstatuspath, indexstatus)


    #copy out in memory file
    if fast:
        modelfile = os.path.join\
            (modeldir, config.getCandidateModelName(modelnum))
        copyoutInMemoryFile(modelfile)
        cleanupInMemoryFile()

    #the model file is in disk now
    nexttextnum = i + 1
    storeModelStatus(modelfile, textnum, nexttextnum)

    indexfile.close()
    #end processing

    #save current progress in status file
    modelnum += 1
    indexstatus['GenerateTextEnd'] = nexttextnum
    indexstatus['GenerateModelEnd'] = modelnum

    utils.sign_epoch(indexstatus, 'Generate')
    utils.store_status(indexstatuspath, indexstatus)


if __name__ == '__main__':
    parser = ArgumentParser(description='Generate model candidates.')
    parser.add_argument('--indexdir', action='store', \
                            help='index directory', \
                            default=config.getTextIndexDir())

    parser.add_argument('--fast', action='store_const', \
                            help='Use in-memory filesystem to speed up generate', \
                            const=True, default=False)


    args = parser.parse_args()
    print(args)
    walkIndexFast(handleOneIndex, args.indexdir, args.fast)
    print('done')
