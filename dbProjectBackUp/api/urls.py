from django.contrib import admin
from django.urls import path,include
from .views import UserGroups,UserProfilePut,UserPvChat


urlpatterns = [
    path("getuserchats",UserGroups.as_view()),
    path("userprofile",UserProfilePut.as_view()),
    path("search",UserPvChat.as_view()),
    path("createpvchat",UserPvChat.as_view())

]
