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

    m_estimates_model = \
        '/media/data/Program/trainer/tools/libpinyin/data/estimates.db'

    def getEstimatesModel(self):
        return self.m_estimates_model

    m_estimate_index = 'estimate.index'

    def getEstimateIndex(self):
        return self.m_estimate_index

    m_sorted_estimate_index = 'estimate.sorted.index'

    def getSortedEstimateIndex(self):
        return self.m_sorted_estimate_index

    m_evals_text = \
        '/media/data/Program/trainer/tools/libpinyin/data/evals.text'

    def getEvalsText(self):
        return self.m_evals_text

    #about 1,200 Chinese characters
    m_minimum_chinese_characters = 1200
    m_minimum_file_size = m_minimum_chinese_characters * 3 + \
        m_minimum_chinese_characters / 2

    def getMinimumFileSize(self):
        return self.m_minimum_file_size

    m_candidate_model_size = 11.9 * 1024 * 1024

    #the trained corpus size of model candidates
    def getCandidateModelSize(self):
        return self.m_candidate_model_size

    m_candidate_model_name = "model-candidates-{0}.db"

    def getCandidateModelName(self, index):
        return self.m_candidate_model_name.format(index)

    m_maximum_occurs_allowed = 20

    def getMaximumOccurs(self):
        return self.m_maximum_occurs_allowed

    m_maximum_increase_rates_allowed = 3.

    def getMaximumIncreaseRates(self):
        return self.m_maximum_increase_rate_allowed
        
    m_segment_postfix = '.segmented'

    def getSegmentPostfix(self):
        return self.m_segment_postfix

    m_segment_report_postfix = '.segment.report'

    def getSegmentReportPostfix(self):
        return self.m_segment_report_postfix

    #For both index page, item page and binary model file
    m_status_postfix = '.status'

    def getStatusPostfix(self):
        return self.m_status_postfix

    m_index_postfix = '.index'

    def getIndexPostfix(self):
        return self.m_index_postfix

    m_text_postfix = '.text'

    def getTextPostfix(self):
        return self.m_text_postfix

    m_final_model_file_name = 'interpolation.text'

    def getFinalModelFileName(self):
        return self.m_final_model_file_name
