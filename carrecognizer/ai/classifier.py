import csv
import datetime
import logging
import random
import time
import json

import numpy as np
from keras.engine.saving import load_model
from keras_preprocessing.image import load_img, img_to_array

from keras import backend as K
from core.models import ClassificationResultItem, ClassificationResult, Classifier, ClassifierItem
from utils.cr_utils import Singleton

logger = logging.getLogger(__name__)

make_model_datafile = "resources/autoscout_makemodel_cache.csv"
make_model__field_names = ['model_id', 'model', 'make_id', 'make']
max_result = 10

classifier_resource_base = "resources/"

CLASS_INDICES_FILENAME = 'class_indices.npy'
MODEL_FILENAME = 'model.h5'
PROPS_FILENAME = 'props.json'
FINAL_PLOT = 'final.png'
TRANSFER_TRAIN_PLOT = 'transfer_train.png'
FINE_TUNE_PLOT = 'fine_tune.png'
SUBPLOTS_DIR = '/plots/'


def load_mocked_make_models():
    make_models = []
    with open(make_model_datafile, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';', fieldnames=make_model__field_names)
        next(reader)
        for row in reader:
            make_models.append(row)
        return make_models


class CleverClassifier(object,  metaclass=Singleton):

    def __init__(self, name):
        self.name = name
        self.base_dir = classifier_resource_base + name + '/'
        self.classifier = None
        if name == 'mock':
            logger.info("Simulating classifier")
            self.make_models = load_mocked_make_models()
        else:
            c = Classifier.objects.filter(is_active=True)
            if len(c) > 0 and c.first().name == self.name:
                logger.info("Classifier %s already exists in db and is active" % self.name)
                self.classifier = c.first()
            else:
                try:
                    c = Classifier.objects.filter(name=self.name)[0]
                    logger.info("Classifier %s found in db, but its not active, activating started" % self.name)
                    self.classifier = self.activate(c)
                except IndexError:
                    logger.info("Classifier %s not found in db creating new")
                    self.classifier = self.create(name)

            if len(Classifier.objects.filter(is_active=True)) != 1:
                raise Exception('Failed to init classifier, there should be exactly 1 active classifier!')

        class_indices_path = self.base_dir + CLASS_INDICES_FILENAME
        self.model_path = self.base_dir + MODEL_FILENAME
        self.img_width, self.img_height = self.classifier.image_width, self.classifier.image_height
        logger.info("Setting up model : %s from %s" % (self.name, self.model_path))
        self.class_dictionary = np.load(class_indices_path, allow_pickle=True).item()
        self.num_classes = len(self.class_dictionary)
        self.inv_map = {v: k for k, v in self.class_dictionary.items()}
        logger.info('Classifier created: %s' % name)

    def activate(self, c):
        for classifier in Classifier.objects.all():
            if classifier.name == c.name:
                classifier.is_active = True
                classifier.active_from = datetime.datetime.now()
                classifier.save()
                c = classifier
                logger.info("Classifier %s activated" % classifier.name)
            elif classifier.is_active:
                classifier.active_to = datetime.datetime.now()
                classifier.is_active = False
                classifier.save()
                logger.info("Classifier %s deacticated" % classifier.name)
        return c

    def create(self, name):
        c = Classifier()
        categories = []
        with open(classifier_resource_base + name + '/' + PROPS_FILENAME) as f:
            data = json.load(f)
            c.name = data['name']
            logger.info("Creating classifier with name %s" % c.name)
            base_dir = classifier_resource_base + c.name + "/"
            for cat in data['categories']:
                categories.append(cat)

            c.description = data['description']
            c.train_size = data['train_size_per_class']
            c.validation_size = data['validation_size_per_class']
            c.test_size = data['test_size_per_class']
            c.image_width = data['img_width']
            c.image_height = data['img_height']
            c.learning_rate = data['lr']
            c.batch_size = data['batch_size']
            c.epochs = data['epochs']
            c.workers = data['workers']
            c.fine_tune_from = data['fine_tune_from']

            c.transfer_train_time = data['transfer_train']['train_time']
            c.transfer_train_accuracy = data['transfer_train']['accuracy']
            c.transfer_train_loss = data['transfer_train']['loss']
            c.transfer_train_plot = base_dir + TRANSFER_TRAIN_PLOT

            c.fine_tune_time = data['fine_tune']['train_time']
            c.fine_tune_accuracy = data['fine_tune']['accuracy']
            c.fine_tune_loss = data['fine_tune']['loss']

            c.test_time = data['test']['run_time']
            c.test_accuracy = data['test']['accuracy']
            c.test_top3_accuracy = data['test']['top3_accuracy']
            c.test_probability = data['test']['avg_probability']

            c.acc = data['acc']
            c.val_acc = data['val_acc']
            c.loss = data['loss']
            c.val_loss = data['val_loss']

            c.raw_json = data

            c.save()
            logger.info("%s saved" % c.name)

            for cat in categories:
                item = ClassifierItem()
                item.name = cat
                item.classifier = c

                cat_data = data['test']['category_results'][cat]
                item.accuracy = cat_data['accuracy']
                item.top3_accuracy = cat_data['top3_accuracy']
                item.avg_probability = cat_data['avg_probabilities']
                item.max_probability = cat_data['max_probabilities']
                item.min_probability = cat_data['min_probabilities']
                item.plot_dir = base_dir + 'plots/' + cat_data['plot'].split('/')[-1]

                item.save()
                logger.info("Classifier item %s saved" % item.name)
        c = self.activate(c)
        return c

    def classify(self, classification_data):
        if self.name == 'mock':
            return self.mocked_classify(classification_data)

        logger.info("Loading model")
        self.model = load_model(self.model_path) # TODO do not clear and load model in every classification..

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
            item = ClassificationResultItem()
            item.name = self.inv_map[predicted_car_id]
            item.accuracy = prediction[predicted_car_id]
            result.add_item(item)
            logger.debug("%s - : %f" % (item.name, item.accuracy))

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
            car = ClassificationResultItem()
            make_model = random.choice(self.make_models)
            car.model = make_model['model']
            car.make = make_model['make']
            car.accuracy = random.randrange(100)
            cars.append(car)

        cars.sort(key=lambda x: x.accuracy, reverse=True)
        for car in cars:
            result.add_item(car)

        # simulate delay
        time.sleep(3)
        return result

