import re
import os
import json
import requests
import logging

from ai.details_handlers import car_query_dictionary
from ai.details_handlers.handler_based import DetailsHandlerBase
# from core.models import ItemDetails, ClassifierItem

from ai.details_handlers.handler_exception import MissingDetailsException
from ai.details_handlers.handler_utils import averaged_list_of_json
from core.models import ItemDetails
from utils.proxy_config import get_random_proxy

logger = logging.getLogger(__name__)


# Serve the details from a specified API: CarQuery
# Can be useful any api based details handler

class CarQueryApiHandler(DetailsHandlerBase):

    base_url = "https://www.carqueryapi.com/api/0.3/"
    query_url = "https://www.carqueryapi.com/api/0.3/?callback=?&cmd=getTrims&make=%s&model=%s" # it needs the make and a model
    details_url = "https://www.carqueryapi.com/api/0.3/?callback=?&cmd=getModel&model=%s" # it needs the model unique id provided by the api

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'Content-Type': 'application/json',
    }

    cache_directory = "logs/details_cache/car_query_cache/"

    def format_server_response(self, response):
        response = re.sub('^\?\(', '', response)
        response = re.sub('\);$', '', response)
        return response

    def create(self, item):
        self.item = item

    def handle(self):
        logger.info("CarQueryApiHandler started to serve the request for item: %s" % self.item.name)
        cached_item = ItemDetails.objects.filter(classifier_item=self.item.id)
        if cached_item:
            logger.info("%s item was cached" % self.item.name)
            return cached_item.first()
        logger.info("%s item not found in cache, CarQuery service started" % self.item.name)

        make, model = self.item.name.split('-')
        cache_file = self.cache_directory + make + "_" + model + ".json"
        if os.path.exists(cache_file):
            with open(cache_file) as json_file:
                json_query_response = json.load(json_file)
        else:
            query_response = requests.get(self.query_url % (make, model), headers=self.headers).text
            query_response = self.format_server_response(query_response)
            json_query_response = json.loads(query_response)
        if 'error' in json_query_response:
            logger.error(json_query_response['error'])
            raise MissingDetailsException(self.item.name)
        make_model_list = json_query_response['Trims']
        details_list = []
        api_call_counter = 0
        for make_model in make_model_list:
            try:
                if api_call_counter > 10:
                    break # due to api limit.. shm
                model_id = make_model['model_id']
                file_path = self.cache_directory + model_id + ".json"
                if os.path.isfile(file_path):
                    with open(file_path) as json_file:
                        json_model_response = json.load(json_file)
                else:
                    model_response = requests.get(self.details_url % model_id, headers=self.headers).text
                    json_model_response = json.loads(self.format_server_response(model_response))
                    api_call_counter += 1

                    with open(file_path, 'w') as outfile:
                        json.dump(json_model_response, outfile)
                details_list.append(json_model_response)
            except Exception as e:
                logger.warning("Skip getting details for modelid because %s" % str(e))
        averaged_details = averaged_list_of_json(details_list)
        non_null_details = {}
        for key, value in averaged_details.items():
            if value is not None:
                non_null_details[key] = value
        if len(non_null_details.keys()) < 1:
            raise MissingDetailsException(self.item.name)

        details = ItemDetails()
        details.details = non_null_details
        details.classifier_item = self.item
        details.save()
        return details



#class TestItem(object):
#     def __init__(self, name):
#         self.name = name
#
#item = TestItem("Audi-TT")
#handler = CarQueryApiHandler()
#handler.create(item)
#result = handler.handle()
#print(result)

