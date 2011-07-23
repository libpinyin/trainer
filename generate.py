#!/usr/bin/python3
import os
import os.path
import subprocess
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
    #begin processing
    cmdline = ['./gen_k_mixture_model', '--maximum-occurs-allowed', \
                   config.getMaximumOccurs(), \
                   '--maximum-increase-rates-allowed', \
                   config.getMaximumIncreaseRates(), \
                   '--k-mixture-model-file', \
                   modelfile, infile]
    subprocess = Popen(cmdline, shell=False, stderr=PIPE, \
                           close_fds=True)

    lines = subprocess.stderr.readlines()
    if lines:
        print('found error report')
        with open(reportfile, 'ab') as f:
            f.writelines(lines)
        f.close()

    os.waitpid(subprocess.pid, 0);
    #end processing


#Note: should check the corpus file size, and skip the too small text file.
def handleOneIndex(indexpath, subdir, indexname):
    print(indexpath, subdir, indexname)

    textnum, modelnum, aggmodelsize = 0, 0, 0
    #begin processing
    indexfile = open(indexpath, 'r')
    for i, oneline in enumerate(indexfile.readlines()):
        #remove trailing '\n'
        oneline = oneline.rstrip(os.linesep)
        (title, textpath) = oneline.split('#')
        infile = config.getTextDir() + textpath
        infilesize = utils.get_file_length(infile)
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
            modelnum++
            modeldir = os.path.join(config.getModelDir(), subdir, indexname)
            modelfile = os.path.join(modeldir, \
                                         config.getCandidateModelName(modelnum))
            reportfile = modelfile + config.getReportPostfix()
            if os.access(modelfile, os.F_OK):
                os.unlink(modelfile)
            if os.access(reportfile, os.F_OK):
                os.unlink(reportfile)
            #save current process in status file
            pass
    indexfile.close()
    #end processing


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
    pass
