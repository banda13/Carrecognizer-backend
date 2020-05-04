import json
import logging

from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from ai.classification_details import ClassificationDetails
from core.models import Classifier
from utils.cr_utils import get_error_response

logger = logging.getLogger(__name__)


class CategoryDetailsView(APIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request, name):
        classifier = Classifier.objects.filter(is_active=True).first()
        if classifier is None:
            logger.error('No classifier is active, please active one')
            return get_error_response("Woopsie no classifier is selected")
        details = ClassificationDetails().get_details(name, classifier)
        return HttpResponse(json.dumps(details))