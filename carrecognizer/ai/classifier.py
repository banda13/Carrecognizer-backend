import logging

logger = logging.getLogger(__name__)


class CleverClassifier(object):

    def __init__(self, name, accuracy, classes, classes_meta):
        self.name = name
        self.accuracy = accuracy
        self.classes = classes
        self.meta = classes_meta
        logger.info('Classifier created: %s' % name)

    def classify(self, image_data):
        logger.info('Classifying image: %s' % image_data.name)
        logger.debug('MOCKED CLASSIFICATION!')
        return {'id': 'bmw', 'accuracy': 100.0, 'result': {'audi': 0, 'bmw': 0, 'asd': 0}}


# 1 base classifier will do the work, but it will be great if we can do it parallel with a lot of classifier
base_classifier = CleverClassifier('mock', 60.0, [], {})