from django.conf.urls import url
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path('classify/', views.Classifier.as_view(), name='classify'),
    path('msg-classify/', views.MessengerClassifier.as_view(), name='messenger-classify'),
    path('classlist/', views.ClassificationList.as_view(), name='classification-list'),
    path('classification/<int:pk>', views.ClassificationDetails.as_view(), name='classification'),
    path(r'file/<username>/<filename>', views.FileHandler.as_view(), name='file'),
    path('webhook/test', views.MessengerWebhook.as_view(), name="messenger")
]