from django.http import HttpResponse
from rest_framework import generics, status
import logging

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Classifier, ClassifierItem
from core.serializers import ClassifierSerializer, ClassifierItemSerializer
from utils.cr_utils import get_error_response

logger = logging.getLogger(__name__)

CLASSIFIER_DIRECTORY = "resources/"
CATEGORIES_PLOT_DIRECTORY = "/plots/"


class ClassifierDetailsView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ClassifierSerializer

    def get(self, request, *args, **kwargs):
        classifier = Classifier.objects.filter(is_active=True).first()
        return Response(self.serializer_class(classifier).data, status=status.HTTP_200_OK)


class ClassifierPlotView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, name):
        classifier = Classifier.objects.filter(is_active=True).first()
        if classifier is None:
            logger.error('No classifier is active, please active one')
            return get_error_response("Woopsie no classifier is selected")
        logger.info("Getting %s plot to classifier %s " %(name, classifier.name))
        full_path = CLASSIFIER_DIRECTORY + classifier.name + '\\' + name
        with open(full_path, 'rb') as f:
            return HttpResponse(f.read(), content_type="image/jpg")


class ClassifierCategoriesView(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ClassifierItemSerializer

    def get_queryset(self):
        classifier = Classifier.objects.filter(is_active=True).first()
        if classifier is None:
            logger.error('No classifier is active, please active one')
            return get_error_response("Woopsie no classifier is selected")
        logger.info("Getting categories for classifier %s " % classifier.name)
        categories = list(ClassifierItem.objects.filter(classifier_id=classifier.id))
        return categories


class CategoryPlotView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, plot):
        classifier = Classifier.objects.filter(is_active=True).first()
        if classifier is None:
            logger.error('No classifier is active, please active one')
            return get_error_response("Woopsie no classifier is selected")

        with open(CLASSIFIER_DIRECTORY + classifier.name + "/plots/" + plot, 'rb') as f:
            return HttpResponse(f.read(), content_type="image/jpg")