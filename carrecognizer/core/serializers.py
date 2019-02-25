from rest_framework import serializers

from core.models import ImageFile, Classifier, Car, Classification, ClassificationFeedback, ClassificationResult, \
    ClassificationResultCar, ClassifierCar
from users.serializers import CustomUserSerializer


class ImageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageFile
        fields = ('id', 'created_at', 'file_name', 'file_path', 'is_deleted',
                  'file_size', 'width', 'height', 'mime_type')


class ClassifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classifier
        fields = ('id', 'name', 'is_active', 'active_from', 'active_to', 'accuracy')


class CarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Car
        fields = ('id', 'make', 'model', 'accuracy')


class ClassificationResultCarSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassificationResultCar
        fields = ('id', 'make', 'model', 'accuracy')


class ClassificationResultSerializer(serializers.ModelSerializer):
    _cars = ClassificationResultCarSerializer(many=True, read_only=True)

    class Meta:
        model = ClassificationResult
        fields = ('id', '_cars')


class ClassificationFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassificationFeedback
        fields = ('id', 'rate', 'comment')


class ClassificationSerializer(serializers.ModelSerializer):
    classifier = ClassifierSerializer(read_only=True)
    creator = CustomUserSerializer(read_only=True)
    image = ImageFileSerializer(read_only=True)
    _results = ClassificationResultSerializer(many=True, read_only=False)
    _feedbacks = ClassificationFeedbackSerializer(many=True, read_only=False)

    class Meta:
        model = Classification
        fields = (
            'id', 'note', 'created_at', 'updated_at','creator', 'classifier', 'image', 'time', '_results', '_feedbacks')


class ClassifierCarSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassifierCar
        fields = ('id', 'make', 'model', 'accuracy')

