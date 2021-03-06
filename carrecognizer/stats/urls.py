from django.urls import path

from stats import views

urlpatterns = [
    path('usage/', views.ApiUsageList.as_view(), name='usage'),
    path('classification_time/', views.ClassificationTimeView.as_view(), name='classification_time'),
]