from ai.classifier import CleverClassifier  # initialize classifier
from django.apps import AppConfig

from carrecognizer.ai.classifier_new import ClassifierNew


class MyAppConfig(AppConfig):
    # base_classifier = CleverClassifier('Haupaca')
    base_classifier = ClassifierNew(160, 160)

    def ready(self):
        pass # Idk when its called, it did not worked for me!
