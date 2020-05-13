import os
import cv2
import time
import json
import requests
import urllib.request
import datetime
import numpy as np

from ai.classification_consts import BASE_IMAGE_DIR, BASE_FILE_MIME, CLASSIFICATION_LOGS
from carrecognizer.apps import MyAppConfig

from core.models import ImageFile, Classification, Classifier
from core.serializers import ClassificationSerializer
from users.models import User
import scipy.ndimage

# helper class to pass the classification process through the system..
#  this will create all necessary object, check permission's etc..
import logging

logger = logging.getLogger(__name__)

class CClassifier(object):

    def __init__(self):
        self.creator = User()
        self.classification = None
        self.image = ImageFile()
        self.classification_result = None
        self.classifier = None

    # main steps of classification
    def find_creator_and_verify_permissions(self, request):
        self.creator = request.user
        asd = User()
        logger.info("%s requested a new classification" % self.creator.email)
        # TODO check permissions
        pass

    def save_picture_and_create_imagedata(self, file):
        logger.info("Processing image file data %s " % file.name)
        try:
            self.image.file_name, self.image.mime_type = os.path.splitext(file.name)
            self.image.file_size = file.size
            if self.image.mime_type is None or self.image.mime_type == "":
                self.image.mime_type = BASE_FILE_MIME
            self.image.file_path = BASE_IMAGE_DIR + self.creator.username + '\\'
            try:
                self.image.width, self.image.height, channels = scipy.ndimage.imread(file).shape
            except Exception as e:
                self.image.width, self.image.height = 0, 0
                logger.warning("Could not identify uploaded image width and height, its ok in facebook uploads")
            self.image.save()
            logger.info("New imagefile saved with id %d " % self.image.id)

            filename = str(self.image.id) + '_' + self.image.file_name

            if not os.path.exists(self.image.file_path):
                os.makedirs(self.image.file_path)
                logger.info("New image directory created for user %s " % self.creator.username)

            with open(self.image.file_path + filename + self.image.mime_type, 'wb+') as img_file:
                for chunk in file.chunks():
                    img_file.write(chunk)
            logger.info("Image saved into %s " % self.image.file_path)
        except Exception as e:
            raise ClassificationException('Failed to save picture', e)

    def save_picture_and_create_imagedata_from_url(self, url):
        logger.info("Processing image file data from %s " % url)
        try:
            self.image.file_name = str(time.time()) + "_facebook"
            self.image.mime_type = ".jpg"
            self.image.file_size = 0
            if self.image.mime_type is None or self.image.mime_type == "":
                self.image.mime_type = BASE_FILE_MIME
            self.image.file_path = BASE_IMAGE_DIR + self.creator.username + '\\'
            try:
                self.image.width, self.image.height, channels = 0, 0, 0
            except Exception as e:
                self.image.width, self.image.height = 0, 0
                logger.warning("Could not identify uploaded image width and height, its ok in facebook uploads")
            self.image.save()
            logger.info("New imagefile saved with id %d " % self.image.id)

            filename = str(self.image.id) + '_' + self.image.file_name

            if not os.path.exists(self.image.file_path):
                os.makedirs(self.image.file_path)
                logger.info("New image directory created for user %s " % self.creator.username)

            urllib.request.urlretrieve(url, self.image.file_path + filename + self.image.mime_type)
            logger.info("Image saved into %s " % self.image.file_path)
        except Exception as e:
            raise ClassificationException('Failed to save picture', e)

    def classify(self):
        try:
            start_time = time.time()
            logger.info('Classification started for image %s by user %s' % (self.image.file_name, self.creator.username))

            self.classifier = Classifier.objects.filter(is_active = True)[0]
            logger.info('Using classifier: %s' % self.classifier.name)

            self.classification = Classification()
            self.classification.creator = self.creator
            self.classification.image = self.image
            self.classification.time = -1
            self.classification.classifier = self.classifier
            self.classification.save()
            logger.info("New classification created with id %d" % self.classification.id)

            self.classification_result = MyAppConfig.base_classifier.classify(self.classification)
            self.classification.time = (time.time() - start_time)
            self.classification.save()
            logger.info('Classification ended at: %s' % str(self.classification.time))
        except Exception as e:
            raise ClassificationException('Failed to classify image', e)

    def serialize(self):
        logger.info('Serializing classification')
        serializer = ClassificationSerializer(self.classification)
        with open(CLASSIFICATION_LOGS + 'classlog_' +str(self.classification.id) + '_' + datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + '.json', 'w') as logfile:
            json.dump(serializer.data, logfile, indent=4)
        return serializer


class ClassificationException(Exception):

    def __init__(self, message, error):
        super().__init__(message)
        logger.error('Classification exception: {}'.format(message), error)