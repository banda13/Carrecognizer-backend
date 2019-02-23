from django.db import models

# from carrecognizer.users.models import CustomUser

# LOOOL django orm didn't hear about one-to-many relationships.. ()


class ImageFile(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=255)
    is_deleted = models.BooleanField()
    file_size = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    mime_type = models.CharField(max_length=50)
    # TODO more complex image propeties can give better evalutaion stats..


class Classifier(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    is_active = models.BooleanField()
    active_from = models.DateTimeField()
    active_to = models.DateTimeField()
    accuracy = models.FloatField()


class Car(models.Model):
    id = models.AutoField(primary_key=True)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    accuracy = models.FloatField()


# fact table
class Classification(models.Model):
    id = models.AutoField(primary_key=True)
    note = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # FIXME needed?
    creator = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    classifier = models.ForeignKey(Classifier, on_delete=models.CASCADE)
    image = models.OneToOneField(ImageFile, on_delete=models.CASCADE)


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


class ClassifierCar(Car):
    classifier = models.ForeignKey(Classifier, on_delete=models.CASCADE)
    pass


class ClassificationResultCar(Car):
    classification_result = models.ForeignKey(ClassificationResult, on_delete=models.CASCADE)
    pass






