from rest_framework import serializers

from .models import User, Strategy

class UserInfoSerializer(serializers.ModelSerializer):
      class Meta:
        model = User
        fields = "__all__"

class StrategySerializer(serializers.ModelSerializer):
    class Meta:
        model=Strategy
        fields="__all__"
        
class LoginSerializer(serializers.Serializer):
    email=serializers.CharField()
    password=serializers.CharField()