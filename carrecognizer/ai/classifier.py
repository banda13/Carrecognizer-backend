import csv
import logging
import random
import time

from core.models import ClassificationResultCar, ClassificationResult

logger = logging.getLogger(__name__)

make_model_datafile = "resources/autoscout_makemodel_cache.csv"
make_model__field_names = ['model_id', 'model', 'make_id', 'make']
max_result = 10

class CleverClassifier(object):

    def __init__(self, name, accuracy, classes, classes_meta):
        self.name = name
        self.accuracy = accuracy
        self.make_models = self.load_mocked_make_models()
        logger.info('Classifier created: %s' % name)

    def load_mocked_make_models(self):
        make_models = []
        with open(make_model_datafile, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';', fieldnames=make_model__field_names)
            next(reader)
            for row in reader:
                make_models.append(row)
            return make_models

    def classify(self, classification_data):
        logger.info('Classifying image: %s' % classification_data.image.file_name)
        logger.debug('MOCKED CLASSIFICATION!')

        result = ClassificationResult()
        classification_data.add_result(result)
        cars = []

        for i in range(max_result):
            car = ClassificationResultCar()
            make_model = random.choice(self.make_models)
            car.model = make_model['model']
            car.make = make_model['make']
            car.accuracy = random.randrange(100)
            cars.append(car)

        cars.sort(key=lambda x: x.accuracy, reverse=True)
        for car in cars:
            result.add_car(car)

        # simulate delay
        time.sleep(3)
        return result


# 1 base classifier will do the work, but it will be great if we can do it parallel with a lot of classifier
base_classifier = CleverClassifier('mock', 60.0, [], {})