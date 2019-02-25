import time
import datetime
import logging
from django.db import models

# from carrecognizer.users.models import CustomUser

# LOOOL django orm didn't hear about one-to-many relationships.. ()

logger = logging.getLogger(__name__)

class ImageFile(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)
    file_size = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    mime_type = models.CharField(max_length=50)
    # TODO more complex image propeties can give better evalutaion stats..


class Classifier(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField()
    active_from = models.DateTimeField()
    active_to = models.DateTimeField()
    accuracy = models.FloatField()

    # objects = models.Manager()


class Car(models.Model):
    id = models.AutoField(primary_key=True)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    accuracy = models.FloatField()

    def __init__(self, make, model, accuracy, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.make = make
        self.model = model
        self.accuracy = accuracy


# fact table
class Classification(models.Model):
    id = models.AutoField(primary_key=True)
    note = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # FIXME needed?
    creator = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    classifier = models.ForeignKey(Classifier, on_delete=models.CASCADE)
    image = models.OneToOneField(ImageFile, on_delete=models.CASCADE)
    time = models.FloatField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._results = None
        self._feedbacks = None

    @property
    def results(self):
        if self._results is None:
            logger.info('Getting classification results')
            self._results = list(ClassificationResult.objects.filter(classification=self))
            logger.debug('%d classification results founded' % len(self._results))
        return self._results

    @results.setter
    def results(self, value):
        raise Exception('DO not set classification results! U can add a new!')

    def add_result(self, result):
        logger.info('Adding new classification result')
        res = self.results # load results if needed
        result.classification = self
        if res is None:
            self._results = []
        self._results.append(result)
        result.save()
        logger.info('Classification result saved with id %d' % result.id)

    @property
    def feedbacks(self):
        if self._feedbacks is None:
            logger.info('Getting classification feedbacks')
            self._feedbacks = list(ClassificationFeedback.objects.filter(classification=self))
            logger.debug('%d feedbacks founded' % len(self._feedbacks))
        return self._feedbacks

    @feedbacks.setter
    def feedbacks(self, value):
        raise Exception('DO not set classification feedbacks! U can add a new!')

    def add_feedback(self, feedback):
        logger.info('Adding new classification feedback')
        fed = self.feedbacks  # load feedbacks if needed
        feedback.classification = self
        if fed is None:
            self._feedbacks = []
        self._feedbacks.append(feedback)
        feedback.save()
        logger.info('Classification feedback saved with id %d' % feedback.id)


class ClassificationFeedback(models.Model):
    id = models.AutoField(primary_key=True)
    rate = models.IntegerField() # user rateing.. 1-10 scale? or?
    comment = models.CharField(max_length=255)
    classification = models.ForeignKey(Classification, on_delete=models.CASCADE)
    # TODO later.. ex share, comments or some social shit.. also can be used to improve AI..


class ClassificationResult(models.Model):
    id = models.AutoField(primary_key=True)
    classification = models.ForeignKey(Classification, on_delete=models.CASCADE, null=False)
    # there can be many result of one 1 classification.. (in ideal case, these are equivalent, but there can be a difference when ai update!)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cars = None

    @property
    def cars(self):
        if self._cars is None:
            logger.info('Getting classification result cars')
            self._results = list(ClassificationResultCar.objects.filter(classification_result=self))
            logger.debug('%d classification cars founded' % len(self._results))
        return self._cars

    @cars.setter
    def cars(self, value):
        raise Exception('DO not set classification result cars! U can only add a new one!')

    def add_car(self, car):
        logger.info('Adding new classification result car')
        c = self.cars  # load results if needed
        car.classification_result = self
        if c is None:
            self._cars = []
        self._cars.append(car)
        car.save()
        logger.info('Classification result car saved with id %d' % car.id)


class ClassificationResultCar(Car):
    classification_result = models.ForeignKey(ClassificationResult, on_delete=models.CASCADE)

    def __init__(self, make, model, accuracy, *args, **kwargs):
        super().__init__(make, model, accuracy, *args, **kwargs)


class ClassifierCar(Car):
    classifier = models.ForeignKey(Classifier, on_delete=models.CASCADE)
    pass


def mockit():

    Classifier.objects.filter(is_active=True).update(is_active=False)


    claazzifier = Classifier()
    claazzifier.accuracy = 100.0
    claazzifier.name = 'mockinto_' + str(time.time())
    claazzifier.active_from = datetime.datetime.now()
    claazzifier.active_to = datetime.datetime(3019, 2, 25)
    claazzifier.is_active = True
    claazzifier.save()

    logger.debug('Mocking done')

mockit()




