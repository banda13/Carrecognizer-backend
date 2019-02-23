from carrecognizer.users.models import CustomUser

# helper class to pass the classification process through the system..
#  this will create all necessary object, check permission's etc..


class CClassifier(object):

    def __init__(self):
        self.creator = None
        self.classification = None
        self.image = None
        self.classification_result = None

    # main steps of classification
    def find_creator_and_verify_permissions(self, requst):
        pass

    def save_picture_and_create_imagedata(self, file):
        pass

    def classify(self):
        # get ai
        # create classification obj
        # classify
        pass

    def create_classification_result(self):
        pass


class ClassificationException(Exception):

    def __init__(self, message, errors):
        super().__init__(message)
        print(errors) # to it better with log!