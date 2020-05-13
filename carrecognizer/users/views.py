import jwt
import datetime
from django.contrib.auth import user_logged_in
from ipware import get_client_ip
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.serializers import jwt_payload_handler

import users
from carrecognizer import settings
from users.models import User
from users.serializers import UserSerializer

import logging

from utils.cr_utils import get_error_response

from utils.security_provider import encode

logger = logging.getLogger(__name__)


class CreateUserAPIView(APIView):
    # Allow any user (authenticated or not) to access this url
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            user = request.data.copy()
            logger.info("Creating new user %s", str(user))

            user['username'] = user['email'].split('@')[0]
            user['password'] = encode(user['password'])

            serializer = UserSerializer(data=user)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            logger.info("New user creation was successful, welcome: %s" % user['username'])
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            msg = "Registration failed: "
            for detail in e.detail.values():
                msg += detail[0] + " "
            logger.exception("Registration failed")
            logger.error(msg)
            return get_error_response(msg)
        except Exception as e:
            logger.error("Registration failed because %s" % str(e), e)
            res = {'error': e}
            return Response(res)


class UserDetailAPI(RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        try:
            if request.user is None:
                return get_error_response("No user provided in the request")
            logger.info("Getting user details: %s" % request.user.username)
            serializer = self.serializer_class(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error("Unexpected server error while getting user details: {}".format(e))
            return get_error_response("Unexpected server error")


class LoginUserAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            email = request.data['email']
            password = encode(request.data['password'])
            ip, is_routable = get_client_ip(request)

            logger.info("Logging in with email %s from ip %s" % (email, ip))

            user = User.objects.get(email=email, password=password)
            if user:
                payload = jwt_payload_handler(user)
                token = jwt.encode(payload, settings.SECRET_KEY)
                user_details = {}
                user_details['username'] = user.username
                user_details['name'] = "%s %s" % (
                    user.first_name, user.last_name)
                user_details['token'] = token
                user_logged_in.send(sender=user.__class__,
                                    request=request, user=user)
                logger.info("User successfully logged in %s" % user_details['username'])

                user.last_login = datetime.datetime.now()
                user.save()
                request.user = user
                return Response(user_details, status=status.HTTP_200_OK)
            else:
                logger.error("User not found with email %s " % email)
                return get_error_response("can not authenticate with the given credentials or the account has been "
                                          "deactivated")
        except KeyError:
            logger.error("Loggin failed because email or password is not provided")
            return get_error_response("please provide a correct email and a password")
        except users.models.User.DoesNotExist:
            logger.error("Unsuccessful login because no user found with the given credentials")
            return get_error_response("The password or email not correct")
        except SyntaxError:
            logger.error("Unsuccessful login because email or password bad formatted")
            return get_error_response("The password or email not correct or bad formatted")
        except Exception:
            logger.exception("Unexpected exception while loggin")
            return get_error_response("Unexpected server error")
