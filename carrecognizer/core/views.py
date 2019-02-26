from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import generics
from rest_framework.decorators import api_view
import logging

from ai.classification import CClassifier
from core.models import Classification
from core.serializers import ClassificationSerializer

logger = logging.getLogger(__name__)

class Classifier(View):

    # @method_decorator(login_required)
    def get(self, request):
        logger.debug('Log whatever you want')
        logger.info('Log this into info..')
        return HttpResponse('hurray, i get a get!')

    @method_decorator(login_required)
    def post(self, request):
        if len(request.FILES) == 0:
            return HttpResponse("Please provide an image", status=400)
        elif len(request.FILES) > 1:
            return HttpResponse("Please provide only 1 image per classification", status=400)

        try:
            myfile = request.FILES['carpic']

            classification = CClassifier()
            classification.find_creator_and_verify_permissions(request)
            classification.save_picture_and_create_imagedata(myfile)
            classification.classify()
            response = classification.serialize()
            return JsonResponse(response.data, safe=False, status=200)
        except MultiValueDictKeyError as e:
            logger.exception('MultiValueDictKeyError')
            return HttpResponse("Please provide an image", status=400)
        except Exception as e:
            logger.exception('Classification error')
            return HttpResponse("Unexpected error while processing image, please try again later!", status=400)


class ClassificationList(generics.ListCreateAPIView):
    model = Classification
    serializer_class = ClassificationSerializer

    def get_queryset(self):
        # NOTE no way to query all classification!
        user = self.request.user
        if user.is_anonymous:
            logger.warning('Could not get classifications for anonymous user')
            return []
        logger.info('Getting %s user classifications' % user.username)
        return Classification.objects.all().filter(creator=user)


class ClassificationDetails(generics.RetrieveAPIView):
    model = Classification
    serializer_class = ClassificationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            logger.warning('Could not get classification for anonymous user')
            return []
        logger.info('Getting %s user classifications for id %d' % user.username)
        return Classification.objects.all().filter(creator=user)