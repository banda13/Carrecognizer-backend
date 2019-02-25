import os
import time

from ai.classification_consts import BASE_IMAGE_DIR, BASE_FILE_MIME
from ai.classifier import CleverClassifier, base_classifier
from core.models import ImageFile, Classification, Classifier
from users.models import CustomUser
import scipy.ndimage

# helper class to pass the classification process through the system..
#  this will create all necessary object, check permission's etc..
import logging

logger = logging.getLogger(__name__)


class CClassifier(object):

    def __init__(self):
        self.creator = CustomUser()
        self.classification = None
        self.image = ImageFile()
        self.classification_result = None
        self.classifier = None

    # main steps of classification
    def find_creator_and_verify_permissions(self, request):
        self.creator = request.user
        asd = CustomUser()
        logger.info("%s requested a new classification" % self.creator.email)
        # TODO check permissions
        pass

    def save_picture_and_create_imagedata(self, file):
        logger.info("Processing image file data %s " % file.name)
        try:
            self.image.file_name, self.image.mime_type = os.path.splitext(file.name)
            self.image.file_size = file.size
            if self.image.mime_type is None:
                self.image.mime_type = BASE_FILE_MIME
            self.image.file_path = BASE_IMAGE_DIR + self.creator.username + '\\'
            self.image.width, self.image.height, channels = scipy.ndimage.imread(file).shape
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

            self.classification_result = base_classifier.classify(self.classification)
            self.classification.time = time.time() - start_time
            logger.info('Classification ended at: %s' % str(self.classification.time))
        except Exception as e:
            raise ClassificationException('Failed to classify image', e)


class ClassificationException(Exception):

    def __init__(self, message, error):
        super().__init__(message)
        logger.error('Classification exception: %s' % message, error)