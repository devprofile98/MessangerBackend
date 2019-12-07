from django.contrib import admin
from django.urls import path,include,re_path
from .views import SignUp,verificator

urlpatterns = [
    path('registration', SignUp.as_view()),
    path('verification', verificator.as_view()),
]
