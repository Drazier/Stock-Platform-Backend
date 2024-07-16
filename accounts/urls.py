from django.contrib import admin
from django.urls import path

from .views import UserInfoView,StrategyView,LoginView,FetchDataView,StrategyAlertView,RsiView

urlpatterns = [
    path("userinfo/", UserInfoView.as_view()),
    path("strategy/", StrategyView.as_view()),
    path("login/",LoginView.as_view()),
    path("fetch/",FetchDataView.as_view()),
    path('strategy_alert/', StrategyAlertView.as_view()),
    path('rsi/',RsiView.as_view())
]
