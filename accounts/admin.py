from django.contrib import admin

# Register your models here.

from .models import User, Strategy

admin.site.register(User)
admin.site.register(Strategy)
