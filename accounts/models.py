from django.db import models
from base.models import BaseModel
from django.conf import settings
from .enums import StrategyType


# Create your models here.


class UserInfo(BaseModel):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=10, unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Strategy(BaseModel):
    user_name = models.ForeignKey(
        UserInfo, on_delete=models.CASCADE, related_name="strategies"
    )
    strategy_name = models.CharField(choices=StrategyType, max_length=100)
    para_1 = models.IntegerField()
    para_2 = models.IntegerField()
    para_3 = models.IntegerField()
    para_4 = models.IntegerField()
