from django.conf.urls import url
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

urlpatterns = [
    path('classify/', views.ClassifierView.as_view(), name='classify'),
    path('msg-classify/', views.MessengerClassifier.as_view(), name='messenger-classify'),
    path('classlist/', views.ClassificationList.as_view(), name='classification-list'),
    path('classification/<int:pk>', views.ClassificationDetailsView.as_view(), name='classification'),
    path(r'file/<username>/<filename>', views.FileHandler.as_view(), name='file'),
    path('classifier/', views.ClassifierDetailsView.as_view(), name='classifier-details'),
    # path('classifier/plot/<name>', views.ClassifierPlotView.as_view(), name='classifier-details')
]