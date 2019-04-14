import time
import datetime
import logging

from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models

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
    description = models.CharField(max_length=255)
    is_active = models.BooleanField()
    active_from = models.DateTimeField()
    active_to = models.DateTimeField()

    train_size = models.IntegerField()
    validation_size = models.IntegerField()
    test_size = models.IntegerField()
    image_width = models.IntegerField()
    image_height = models.IntegerField()

    learning_rate = models.FloatField()
    batch_size = models.IntegerField()
    epochs = models.IntegerField()
    workers = models.IntegerField()
    fine_tune_from = models.IntegerField()

    transfer_train_time = models.IntegerField()
    transfer_train_accuracy = models.FloatField()
    transfer_train_loss = models.FloatField()

    fine_tune_time = models.IntegerField()
    fine_tune_accuracy = models.FloatField()
    fine_tune_loss = models.FloatField()

    test_accuracy = models.FloatField()
    test_time = models.FloatField()
    test_top3_accuracy = models.FloatField()
    test_probability = models.FloatField()

    acc = JSONField()  # its postgresql specific!!
    val_acc = JSONField()
    loss = JSONField()
    val_loss = JSONField()
    raw_json = JSONField()


# fact table
class Classification(models.Model):
    id = models.AutoField(primary_key=True)
    note = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # FIXME needed?
    creator = models.ForeignKey('users.User', on_delete=models.CASCADE)
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
            self._results = []
            logger.info('Getting classification results')
            temp_res = list(ClassificationResult.objects.filter(classification=self))
            for r in temp_res:
                c = r.items
                self._results.append(r)
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
        self._items = None

    @property
    def items(self):
        if self._items is None:
            logger.info('Getting classification result items')
            self._items = list(ClassificationResultItem.objects.filter(classification_result=self))
            logger.debug('%d classification items founded' % len(self._items))
        return self._items

    @items.setter
    def items(self, value):
        raise Exception('DO NOT set classification result items! U can only add a new one!')

    def add_item(self, item):
        logger.info('Adding new classification result item')
        c = self.items  # load results if needed
        item.classification_result = self
        if c is None:
            self._items = []
        self._items.append(item)
        item.save()
        logger.info('Classification result item saved with id %d' % item.id)


class ClassificationResultItem(models.Model):
    classification_result = models.ForeignKey(ClassificationResult, on_delete=models.CASCADE)
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    accuracy = models.FloatField(default=-1)


class ClassifierItem(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    accuracy = models.FloatField()
    top3_accuracy = models.FloatField()
    avg_probability = models.FloatField()
    max_probability = models.FloatField()
    min_probability = models.FloatField()
    plot_dir = models.CharField(max_length=255)
    classifier = models.ForeignKey(Classifier, on_delete=models.CASCADE)





