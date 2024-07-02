from django.contrib import admin
from django.urls import path

from .views import UserInfoView, StrategyView,LoginView

urlpatterns = [
 

    path("userinfo/", UserInfoView.as_view()),
    path("strategy/", StrategyView.as_view()),
    path("login/",LoginView.as_view()),
]
