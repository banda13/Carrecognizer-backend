from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import generics
from rest_framework.decorators import api_view
import logging

from ai.classification import CClassifier

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
            return HttpResponse("Please provide an image")
        elif len(request.FILES) > 1:
            return HttpResponse("Please provide only 1 image per classification")
        else:
            print("Some files are in the request, processing started..")

        try:
            myfile = request.FILES['carpic']

            classification = CClassifier()
            classification.find_creator_and_verify_permissions(request)
            classification.save_picture_and_create_imagedata(myfile)
            return HttpResponse('oki')
        except MultiValueDictKeyError as e:
            print(e)  # TODO log
            return HttpResponse("Please provide an image")
        except Exception as e:
            print(e)
            return HttpResponse("Unexpected error while processing image, please try again later!")


class ClassificationList(generics.ListAPIView):
    pass