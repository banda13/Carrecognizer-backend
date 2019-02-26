from django.conf.urls import url
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path('classify/', views.Classifier.as_view(), name='classify'),
    path('classlist/', views.ClassificationList.as_view(), name='classification-list'),
    path('classification/<int:pk>', views.ClassificationDetails.as_view(), name='classification'),
]