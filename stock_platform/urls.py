from django.contrib import admin
from django.urls import path, include
from .views import SuccessView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", SuccessView.as_view(), name="success"),
    path("api/", include("accounts.urls")),
]
