from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic, View

from .forms import CustomUserCreationForm


class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'


class UserProfile(View):

    def get(self, request):
        return request.user