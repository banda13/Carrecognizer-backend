import csv
import logging
import random
import time

import numpy as np
from keras.engine.saving import load_model
from keras_preprocessing.image import load_img, img_to_array

from keras import backend as K
from core.models import ClassificationResultCar, ClassificationResult

logger = logging.getLogger(__name__)

make_model_datafile = "resources/autoscout_makemodel_cache.csv"
make_model__field_names = ['model_id', 'model', 'make_id', 'make']
max_result = 10

classifier_resource_base = "resources/"

class CleverClassifier(object):

    def __init__(self, name):
        self.name = name
        if name == 'mock':
            logger.info("Simulating classifier")
            self.make_models = self.load_mocked_make_models()
        else:
            class_indices_path = classifier_resource_base + name + "/" + name + "_class_indices.npy"
            self.model_path = classifier_resource_base + name + "/" + name + ".h5"
            self.img_width, self.img_height = 150, 150

            logger.info("Setting up model : %s from %s" % (self.name, self.model_path))
            self.class_dictionary = np.load(class_indices_path).item()
            self.num_classes = len(self.class_dictionary)
            self.inv_map = {v: k for k, v in self.class_dictionary.items()}
            # self.model = load_model(model_path)
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
        if self.name == 'mock':
            return self.mocked_classify(classification_data)

        logger.info("Loading model")
        self.model = load_model(self.model_path)

        logger.info("Preprocessing image %s " % classification_data.image.file_name)
        image = load_img(classification_data.image.file_path + str(classification_data.image.id) + "_" +  classification_data.image.file_name  + classification_data.image.mime_type, target_size=(self.img_width, self.img_height))
        image = img_to_array(image)
        image = image / 255
        image = np.expand_dims(image, axis=0)

        logger.info('Classifying image: %s' % classification_data.image.file_name)
        prediction_start = time.time()
        prediction = self.model.predict(image).reshape(self.num_classes)

        logger.info("Prediction done at %s, processing results" % (str(time.time() - prediction_start)))
        idx_prediction = np.argsort(-prediction, axis=0)

        result = ClassificationResult()
        classification_data.add_result(result)
        for predicted_car_id in idx_prediction:
            car = ClassificationResultCar()
            car.make = 'Audi'
            car.model = self.inv_map[predicted_car_id]
            car.accuracy = prediction[predicted_car_id]
            result.add_car(car)
            logger.debug("%s - %s : %d" % (car.make, car.model, car.accuracy))

        logger.info("Clearing keras session")
        K.clear_session()

        logger.info("Classification done")
        return result

    def mocked_classify(self, classification_data):
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
base_classifier = CleverClassifier('Dufegno')