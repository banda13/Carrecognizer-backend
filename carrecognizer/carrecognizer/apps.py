from ai.classifier import CleverClassifier  # initialize classifier
from django.apps import AppConfig


class MyAppConfig(AppConfig):
    base_classifier = CleverClassifier('TrarTar')

    def ready(self):
        pass # Idk when its called, it did not worked for me!
