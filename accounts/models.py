from django.db import models
from base.models import BaseModel
from  django.contrib.auth.models import AbstractUser,BaseUserManager
from django.conf import settings
from .enums import StrategyType
import uuid


# Create your models here.

class CustomUserManager(BaseUserManager):
    def get_queryset(self):
        """
        Returns a queryset that excludes records with a non-null deleted_at field.

        Returns:
            QuerySet: The queryset excluding soft-deleted records.
        """
        return super().get_queryset().filter(deleted_at=None)

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser,BaseModel):
    email = models.EmailField(unique=True)
    user_name = models.CharField(max_length=150, blank=True)
    phone_no = models.CharField(max_length=12, unique=True, null=True, blank=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Strategy(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="strategies"
    )
    strategy_name = models.CharField(choices=StrategyType, max_length=100)
    para_1 = models.IntegerField()
    para_2 = models.IntegerField(blank=True, null=True)
    para_3 = models.IntegerField(blank=True, null=True)
    para_4 = models.IntegerField(blank=True, null=True)
