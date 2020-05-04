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
    description = models.CharField(max_length=255, null=True)
    is_active = models.BooleanField(default=False)
    active_from = models.DateTimeField(null=True)
    active_to = models.DateTimeField(null=True)

    train_size = models.IntegerField()
    validation_size = models.IntegerField()
    test_size = models.IntegerField(null=True)
    image_width = models.IntegerField()
    image_height = models.IntegerField()

    learning_rate = models.FloatField(null=True)
    batch_size = models.IntegerField(null=True)
    epochs = models.IntegerField(null=True)
    workers = models.IntegerField(null=True)
    fine_tune_from = models.IntegerField(null=True)
    final_plot = models.CharField(max_length=255, null=True)

    transfer_train_time = models.IntegerField(null=True)
    transfer_train_accuracy = models.FloatField(null=True)
    transfer_train_loss = models.FloatField(null=True)
    transfer_train_plot = models.CharField(max_length=255, null=True)

    fine_tune_time = models.IntegerField(null=True)
    fine_tune_accuracy = models.FloatField(null=True)
    fine_tune_loss = models.FloatField(null=True)
    fine_tune_plot = models.CharField(max_length=255, null=True)

    test_accuracy = models.FloatField(null=True)
    test_time = models.FloatField(null=True)
    test_top3_accuracy = models.FloatField(null=True)
    test_probability = models.FloatField(null=True)

    acc = JSONField(null=True)  # its postgresql specific!!
    val_acc = JSONField(null=True)
    loss = JSONField(null=True)
    val_loss = JSONField(null=True)
    raw_json = JSONField(null=True)


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
            temp_res = list(ClassificationResult.objects.filter(classification=self))
            for r in temp_res:
                c = r.items
                self._results.append(r)
            # logger.debug('%d classification results founded' % len(self._results))
        return self._results

    @results.setter
    def results(self, value):
        raise Exception('DO not set classification results! U can add a new!')

    def add_result(self, result):
        logger.debug('Adding new classification result %s' % str(result))
        res = self.results # load results if needed
        result.classification = self
        if res is None:
            self._results = []
        self._results.append(result)
        result.save()
        logger.debug('Classification result saved with id %d' % result.id)

    @property
    def feedbacks(self):
        if self._feedbacks is None:
            self._feedbacks = list(ClassificationFeedback.objects.filter(classification=self))
            logger.debug('%d feedbacks founded' % len(self._feedbacks))
        return self._feedbacks

    @feedbacks.setter
    def feedbacks(self, value):
        raise Exception('DO not set classification feedbacks! U can add a new!')

    def add_feedback(self, feedback):
        logger.debug('Adding new classification feedback %s' % str(feedback))
        fed = self.feedbacks  # load feedbacks if needed
        feedback.classification = self
        if fed is None:
            self._feedbacks = []
        self._feedbacks.append(feedback)
        feedback.save()
        logger.debug('Classification feedback saved with id %d' % feedback.id)


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
            self._items = list(ClassificationResultItem.objects.filter(classification_result=self))
        return self._items

    @items.setter
    def items(self, value):
        raise Exception('DO NOT set classification result items! U can only add a new one!')

    def add_item(self, item):
        logger.debug('Adding new classification result item %s' % str(item))
        c = self.items  # load results if needed
        item.classification_result = self
        if c is None:
            self._items = []
        self._items.append(item)
        item.save()
        logger.debug('Classification result item saved with id %d' % item.id)


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


class ItemDetails(models.Model):
    id = models.AutoField(primary_key=True)
    classifier_item = models.ForeignKey(ClassifierItem, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    details = JSONField(null=True)




