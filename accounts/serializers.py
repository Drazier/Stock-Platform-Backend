from rest_framework import serializers

from .models import User, Strategy

class UserInfoSerializer(serializers.ModelSerializer):
      class Meta:
        model = User
        fields = "__all__"

class StrategySerializer(serializers.Serializer):
    user_name = serializers.CharField(error_messages={"required": "User name is required"})
    strategy_name = serializers.CharField(error_messages={"required": "Strategy name is required"})
    para_1 = serializers.IntegerField()
    para_2 = serializers.IntegerField()
    para_3 = serializers.IntegerField()
    para_4 = serializers.IntegerField()

    