from rest_framework import status
from rest_framework.response import Response


def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def get_error_response(message, details='No details provided'):
    res = {'error': message, 'details': details}
    return Response(res, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
