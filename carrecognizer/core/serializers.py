from rest_framework import serializers

from core.models import ImageFile, Classifier, Classification, ClassificationFeedback, ClassificationResult, \
    ClassificationResultItem, ClassifierItem
from users.serializers import UserSerializer


class ImageFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageFile
        fields = ('id', 'created_at', 'file_name', 'file_path', 'is_deleted',
                  'file_size', 'width', 'height', 'mime_type')


class SimpleClassifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classifier
        fields = ('id', 'name')

class ClassifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classifier
        fields = ('id', 'name')

class ClassificationResultItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassificationResultItem
        fields = ('id', 'name', 'accuracy')


class ClassificationResultSerializer(serializers.ModelSerializer):
    _items = ClassificationResultItemSerializer(many=True, read_only=True)

    class Meta:
        model = ClassificationResult
        fields = ('id', '_items')


class ClassificationFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassificationFeedback
        fields = ('id', 'rate', 'comment')


class ClassificationSerializer(serializers.ModelSerializer):
    classifier = SimpleClassifierSerializer(read_only=True)
    creator = UserSerializer(read_only=True)
    image = ImageFileSerializer(read_only=True)
    _results = ClassificationResultSerializer(many=True, read_only=False)
    _feedbacks = ClassificationFeedbackSerializer(many=True, read_only=False)

    class Meta:
        model = Classification
        fields = (
            'id', 'note', 'created_at', 'updated_at','creator', 'classifier', 'image', 'time', '_results', '_feedbacks')


class ClassifierItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassifierItem
        fields = ('id', 'name', 'accuracy')

