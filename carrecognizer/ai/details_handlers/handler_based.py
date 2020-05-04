from abc import ABC, abstractmethod

from ai.details_handlers.handler_exception import HandlerInitializationException

# USAGE:
# All handler MUST have to extend from this base handler, and override the following methods
# In create it gets and ClassifierItem. Process it and get all the info you need.
# In handle try to get details for the category
# If it exists it MUST return an ItemDetails instance
# If its missing the throw a MissingDetailsException exception


class DetailsHandlerBase(ABC):

    def __init__(self):
        self.item = None

    @abstractmethod
    def create(self, item):
        raise HandlerInitializationException("create was not overridden")

    @abstractmethod
    def handle(self):
        raise HandlerInitializationException("handle was not overridden")
