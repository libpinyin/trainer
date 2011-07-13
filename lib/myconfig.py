import os


class MyConfig:
    ''' My Configuration '''

    m_current_pass_epoch = 1

    def getEpoch(self):
        return m_current_pass_epoch

    m_trainer_dir = '/media/data/Program/trainer'

    def getBaseDir(self):
        return m_trainer_dir

    def getTextDir(self):
        return m_trainer_dir + os.sep + 'texts'

    def getModelDir(self):
        return m_trainer_dir + os.sep + 'models'

    def getFinalModelDir(self):
        return m_trainer_dir + os.sep + 'final'

    #about 1,200 Chinese characters
    m_minimum_file_size = 5,000

    def getMinimumFileSize(self):
        return m_minimum_file_size

    m_segment_postfix = '.segmented'

    def getSegmentPostfix(self):
        return m_segment_postfix

    #For both index page, item page and binary model file
    m_status_postfix = '.status'

    def getStatusPostfix(self):
        return m_status_postfix
