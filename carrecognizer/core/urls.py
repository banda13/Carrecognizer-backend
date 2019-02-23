from django.urls import path

from . import views

urlpatterns = [
    path('classify/', views.Classifier.as_view(), name='classify'),
]