import jwt
import datetime
from django.contrib.auth import user_logged_in
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic, View
from ipware import get_client_ip
from rest_framework import status
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.serializers import jwt_payload_handler

from carrecognizer import settings
from users.models import User
from users.serializers import UserSerializer

import logging

logger = logging.getLogger(__name__)

class CreateUserAPIView(APIView):
    # Allow any user (authenticated or not) to access this url
    permission_classes = (AllowAny,)

    def post(self, request):
        user = request.data
        logger.info("Creating new user", user)

        user['username'] = user['email'].split('@')[0]

        serializer = UserSerializer(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        logger.info("New user creation was successful, welcome: %s" % user['username'])
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserDetailAPI(RetrieveAPIView):
    # Allow only authenticated users to access this url
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        if request.user is None:
            return Response("No user provided in the request", status=status.HTTP_401_UNAUTHORIZED)
        logger.info("Getting user details", request.user)
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LoginUserAPIView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            email = request.data['email']
            password = request.data['password'] # TODO encode this!
            ip, is_routable = get_client_ip(request)
            referer = request.META['HTTP_REFERER']

            logger.info("Logging in with email %s from %s, ip %s" % (email, referer, ip))

            user = User.objects.get(email=email, password=password)
            if user:
                try:
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
                    return Response(user_details, status=status.HTTP_200_OK)

                except Exception as e:
                    logger.exception("Unexpected exception while logging in", e)
                    raise e
            else:
                logger.error("User not found with email %s " % email)
                res = {
                    'error': 'can not authenticate with the given credentials or the account has been deactivated'}
                return Response(res, status=status.HTTP_403_FORBIDDEN)
        except KeyError:
            logger.error("Loggin failed because email or password is not provided")
            res = {'error': 'please provide a email and a password'}
            return Response(res)
