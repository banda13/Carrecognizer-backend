from django.conf.urls import url
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from core.view.classifier_views import ClassifierDetailsView, ClassifierPlotView, ClassifierCategoriesView, \
    CategoryPlotView
from core.view.details_views import CategoryDetailsView
from . import views

urlpatterns = [
    path('classify/', views.ClassifierView.as_view(), name='classify'),
    path('msg-classify/', views.MessengerClassifier.as_view(), name='messenger-classify'),
    path('classlist/', views.ClassificationList.as_view(), name='classification-list'),
    path('classification/<int:pk>', views.ClassificationDetailsView.as_view(), name='classification'),
    path(r'file/<username>/<filename>', views.FileHandler.as_view(), name='file'),

    path('classifier/', ClassifierDetailsView.as_view(), name='classifier-details'),
    path('classifier/plot/<name>', ClassifierPlotView.as_view(), name='classifier-plot'),
    path('categories/', ClassifierCategoriesView.as_view(), name='categories'),
    path('categories/plot/<plot>', CategoryPlotView.as_view(), name='categories-plot'),

    path('category/<name>', CategoryDetailsView.as_view(), name='category-details')

]