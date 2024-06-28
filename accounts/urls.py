from django.contrib import admin
from django.urls import path

from .views import UserInfoView, StrategyView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("userinfo/", UserInfoView.as_view()),
    path("strategy/", StrategyView.as_view()),
]
