from django.contrib import admin

# Register your models here.

from .models import UserInfo, Strategy

admin.site.register(UserInfo)
admin.site.register(Strategy)
