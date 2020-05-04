import logging

logger = logging.getLogger(__name__)


class HandlerInitializationException(Exception):

    def __init__(self, message):
        super().__init__(message)
        logger.error("Details handler initialization failed " + message)


class HandlerException(Exception):

    def __init__(self, message):
        super().__init__(message)
        logger.error("Details handler error" + message)


class MissingDetailsException(Exception):

    def __init__(self, message):
        super().__init__(message)
        logger.error("Missing details for category: " + message)