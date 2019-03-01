from django.urls import path

from users.views import CreateUserAPIView, UserDetailAPI, LoginUserAPIView
from . import views

urlpatterns = [
    path('create/', CreateUserAPIView.as_view()),
    path('profile/', UserDetailAPI.as_view()),
    path('login/', LoginUserAPIView.as_view()),
]