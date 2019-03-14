import mimetypes
import os

from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.db.models.functions import Cast
from django.forms import CharField
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import generics
from rest_framework.decorators import api_view
from django.db.models import Q
import logging

from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

from ai.classification import CClassifier
from ai.classification_consts import BASE_IMAGE_DIR
from core.models import Classification
from core.serializers import ClassificationSerializer
logger = logging.getLogger(__name__)

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

class MessengerWebhook(APIView):
    permission_classes = (AllowAny,)

    def get(self, request):
        logger.info("Messenger GET called")
        return HttpResponse("GET EVENT RECEIVED", 200)

    def post(self, request):
        logger.info("Messenger POST called")
        return HttpResponse("POST EVENT RECEIVED", 200)

    def handleMessage(self):
        pass

    def handlePostBacks(self):
        pass

    def callSendAPI(self):
        pass

class Classifier(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        logger.debug('Log whatever you want')
        logger.info('Log this into info..')
        return HttpResponse('hurray, i get a get!')


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
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # NOTE no way to query all classification!
        user = self.request.user
        if user.is_anonymous:
            logger.warning('Could not get classifications for anonymous user')
            return []
        logger.info('Getting %s user classifications' % user.username)
        filter = self.request.GET.get('filter', '')
        order = self.request.GET.get('orderby', 'id')
        order_val = self.request.GET.get('order_val', 'asc')  # asc or desc

        response = []

        if filter is not None and filter != '':
            q = SearchQuery(filter)
            vector = SearchVector('image__file_name') # + ..

            classifications = Classification.objects.annotate(search = vector).filter(search=q).filter(creator=user).order_by('-' + order) if order_val == 'desc' else Classification.objects.annotate(search = vector).filter(search=q).filter(creator=user)
            for c in classifications:
                r = c.results
                response.append(c) # lazy loading ehh
        else:
            classifications = (Classification.objects.filter(creator=user).order_by('-' + order) if order_val == 'desc' else Classification.objects.filter(creator=user))
            for c in classifications:
                r = c.results
                response.append(c)
        return response

    def get_context_data(self, **kwargs):
        context = super(ClassificationList, self).get_context_data(**kwargs)
        context['filter'] = self.request.GET.get('filter', '')
        context['orderby'] = self.request.GET.get('orderby', '')
        context['order_val'] = self.request.GET.get('order_val', 'asc')
        return context


class ClassificationDetails(generics.RetrieveAPIView):
    model = Classification
    serializer_class = ClassificationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.is_anonymous:
            logger.warning('Could not get classification for anonymous user')
            return []
        logger.info('Getting %s user classifications for id %d' % user.username)
        return Classification.objects.all().filter(creator=user)


class FileHandler(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, username, filename):
        logger.info("Downloading image %s image: %s" % (username,filename))

        full_path = BASE_IMAGE_DIR + username + '\\' + filename
        with open(full_path, 'rb') as f:
            return HttpResponse(f.read(), content_type="image/jpg")
