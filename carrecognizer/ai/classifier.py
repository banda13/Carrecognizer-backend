import logging

from core.models import ClassificationResultCar, ClassificationResult

logger = logging.getLogger(__name__)


class CleverClassifier(object):

    def __init__(self, name, accuracy, classes, classes_meta):
        self.name = name
        self.accuracy = accuracy
        self.classes = classes
        self.meta = classes_meta
        logger.info('Classifier created: %s' % name)

    def classify(self, classification_data):
        logger.info('Classifying image: %s' % classification_data.image.file_name)
        logger.debug('MOCKED CLASSIFICATION!')
        main_car = ClassificationResultCar('bmw', 'M5', 100.0)
        secondary_car = ClassificationResultCar('audi', 'A3', 0.0)
        secondary_car2 = ClassificationResultCar('adui', 'A5', 0.1)
        result = ClassificationResult()
        classification_data.add_result(result)
        logger.info('New Classification result created')

        result.add_car(main_car)
        result.add_car(secondary_car)
        result.add_car(secondary_car2)
        logger.info("Classification cars saved..")
        return result


# 1 base classifier will do the work, but it will be great if we can do it parallel with a lot of classifier
base_classifier = CleverClassifier('mock', 60.0, [], {})