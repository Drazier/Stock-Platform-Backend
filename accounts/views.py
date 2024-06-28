from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import UserInfo, Strategy
from .serializers import UserInfoSerializer, StrategySerializer
from base.views import HandleException
from rest_framework import status

# Create your views here.


class UserInfoView(HandleException, APIView):
    def get(self, request):
        data = UserInfo.objects.all()
        serializer = UserInfoSerializer(data, many=True)
        return Response(
            {"status": True, "data": serializer.data}, status=status.HTTP_200_OK
        )

    def post(self, request):
        data = request.data
        serializer = UserInfoSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        name = serializer.validated_data["name"]
        email = serializer.validated_data["email"]
        mobile = serializer.validated_data["mobile"]
        password = serializer.validated_data["password"]
        UserInfo.objects.create(
            name=name, email=email, mobile=mobile, password=password
        )
        return Response(
            {"status": True, "message": "Data saved successfully"},
            status=status.HTTP_201_CREATED,
        )

    def patch(self, request):
        data = request.data
        serializer = UserInfoSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        name = serializer.validated_data["name"]
        mobile = serializer.validated_data["mobile"]
        password = serializer.validated_data["password"]
        UserInfo.objects.filter(email=email).update(
            name=name, mobile=mobile, password=password
        )
        return Response(
            {"status": True, "message": "Data updated successfully"},
            status=status.HTTP_200_OK,
        )

    def delete(self, request):
        data = request.data
        serializer = UserInfoSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        UserInfo.objects.filter(email=email).delete()
        return Response(
            {"status": True, "message": "Data deleted successfully"},
            status=status.HTTP_200_OK,
        )


class StrategyView(HandleException, APIView):

    def get(self, request):
        data = Strategy.objects.all()
        serializer = StrategySerializer(data, many=True)
        return Response(
            {"status": True, "message": serializer.data}, status=status.HTTP_200_OK
        )

    def post(self, request):
        data = request.data
        serializer = StrategySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user_name = serializer.validated_data["user_name"]
        strategy_name = serializer.validated_data["strategy_name"]
        para_1 = serializer.validated_data["para_1"]
        para_2 = serializer.validated_data["para_2"]
        para_3 = serializer.validated_data["para_3"]
        para_4 = serializer.validated_data["para_4"]
        Strategy.objects.create(
            user_name=user_name,
            strategy_name=strategy_name,
            para_1=para_1,
            para_2=para_2,
            para_3=para_3,
            para_4=para_4,
        )
        return Response(
            {"status": True, "message": "Data saved successfully"},
            status=status.HTTP_201_CREATED,
        )

    def patch(self, request):
        data = request.data
        serializer = StrategySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user_name = serializer.validated_data["user_name"]
        strategy_name = serializer.validated_data["strategy_name"]
        para_1 = serializer.validated_data["para_1"]
        para_2 = serializer.validated_data["para_2"]
        para_3 = serializer.validated_data["para_3"]
        para_4 = serializer.validated_data["para_4"]
        Strategy.objects.filter(user_name=user_name).update(
            strategy_name=strategy_name,
            para_1=para_1,
            para_2=para_2,
            para_3=para_3,
            para_4=para_4,
        )
        return Response(
            {"status": True, "message": "Data updated successfully"},
            status=status.HTTP_200_OK,
        )

    def delete(self, request):
        data = request.data
        serializer = StrategySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user_name = serializer.validated_data["user_name"]
        Strategy.objects.filter(user_name=user_name).delete()
        return Response(
            {"status": True, "message": "Data deleted successfully"},
            status=status.HTTP_200_OK,
        )
