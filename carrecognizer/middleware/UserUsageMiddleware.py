import logging

from stats.models import ApiUsage

logger = logging.getLogger(__name__)


class UserUsageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):

        logger.info('[%s] -> [%s]' % (request.user.username, request.META['PATH_INFO']))
        response = self.get_response(request)
        usage = ApiUsage()
        user = request.user
        usage.username = user.username
        usage.email = user.email if user.is_authenticated else None
        usage.last_login = user.last_login if user.is_authenticated else None
        usage.referer = request.META.get('HTTP_REFERER')
        usage.method = request.META.get('REQUEST_METHOD')
        usage.path = request.path
        usage.user_agent = request.META.get('HTTP_USER_AGENT')
        usage.query_string = request.META.get('QUERY_STRING')
        usage.origin = request.META.get('HTTP_ORIGIN')
        usage.host = request.META.get('HTTP_HOST')
        usage.content_type = request.content_type
        usage.remote_address = request.META.get('REMOTE_ADDR')
        usage.scheme = request.scheme
        usage.response_code = response.status_code
        usage.save()

        return response
