import logging

from ai.details_handlers import car_query_dictionary
from ai.details_handlers.car_query_handler import CarQueryApiHandler
from core.models import Classifier, ClassifierItem

logger = logging.getLogger(__name__)


class ClassificationDetails(object):

    # can support multiple handlers but then need to merge the results
    handler = CarQueryApiHandler()

    def get_details(self, name, classifier):
        item = ClassifierItem.objects.filter(name=name, classifier=classifier.id)
        if not item:
            logger.error("Missing category %s" % name)
            return {}
        self.handler.create(item.first())
        result = self.handler.handle()
        translated_details = {}
        for key, value in result.details.items():
            if key in car_query_dictionary.eng and value is not None:
                translated_details[car_query_dictionary.eng[key]] = value
        return translated_details
