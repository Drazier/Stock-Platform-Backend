from django.contrib import admin
from django.urls import path

from .views import UserInfoView,StrategyView,LoginView,FetchDataView,StrategyAlertView,Rsi,Macd,Ema,Sma,Adx,BB,KC

urlpatterns = [
    path('userinfo/', UserInfoView.as_view()),
    path('strategy/', StrategyView.as_view()),
    path('login/',LoginView.as_view()),
    path('fetch/',FetchDataView.as_view()),
    path('strategy_alert/', StrategyAlertView.as_view()),
    path('rsi/',Rsi.as_view()),
    path('macd/',Macd.as_view()),
    path('ema/',Ema.as_view()),
    path('sma/',Sma.as_view()),
    path('bb/',BB.as_view()),
    path('adx/',Adx.as_view()),
    path('kc/',KC.as_view()),
]
