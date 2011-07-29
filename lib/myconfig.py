import os


class MyConfig:
    ''' My Configuration '''

    m_current_epoch = {'SegmentEpoch': 1, \
                           'GenerateEpoch': 2, \
                           'EstimateEpoch': 3, \
                           'PruneEpoch': 4, \
                           'EvaluateEpoch': 5 \
                           }

    def getEpochs(self):
        return self.m_current_epoch

    m_trainer_dir = '/media/data/Program/trainer'

    def getBaseDir(self):
        return self.m_trainer_dir

    def getTextDir(self):
        return self.m_trainer_dir + os.sep + 'texts'

    def getModelDir(self):
        return self.m_trainer_dir + os.sep + 'models'

    def getFinalModelDir(self):
        return self.m_trainer_dir + os.sep + 'finals'

    m_tools_dir = '/media/data/Program/trainer/tools/libpinyin'

    def getToolsDir(self):
        return self.m_tools_dir

    m_evals_dir = '/media/data/Program/trainer/evals/libpinyin'

    def getEvalsDir(self):
        return self.m_evals_dir

    def getEstimatesModel(self):
        estimates_model = self.m_tools_dir + '/data/estimates.db'
        return estimates_model

    def getEstimateIndex(self):
        return 'estimate.index'

    def getSortedEstimateIndex(self):
        return 'estimate.sorted.index'

    def getEvalsText(self):
        evals_text = m_evals_dir + '/data/evals.text'
        return evals_text

    def getMinimumFileSize(self):
        #about 1,200 Chinese characters
        minimum_chinese_characters = 1200
        minimum_file_size = minimum_chinese_characters * 3 + \
            minimum_chinese_characters / 2

        return minimum_file_size

    #the trained corpus size of model candidates
    def getCandidateModelSize(self):
        candidate_model_size = 11.9 * 1024 * 1024 * 2
        return candidate_model_size

    def getModelPostfix(self):
        return '.db'

    def getCandidateModelName(self, index):
        candidate_model_name = "model-candidates-{0}.db"
        return candidate_model_name.format(index)

    def getMaximumOccursAllowed(self):
        return 20

    def getMaximumIncreaseRatesAllowed(self):
        return 3.

    def getReportPostfix(self):
        return '.report'

    def getSegmentPostfix(self):
        return '.segmented'

    def getSegmentReportPostfix(self):
        return '.segment.report'

    #For both index page, item page and binary model file
    def getStatusPostfix(self):
        return '.status'

    def getIndexPostfix(self):
        return '.index'

    def getTextPostfix(self):
        return '.text'

    def getFinalModelFileName(self):
        return 'interpolation.text'

    def getFinalStatusFileName(self):
        return 'cwd.status'
