from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import User, Strategy
from .serializers import UserInfoSerializer, StrategySerializer
from base.views import HandleException
from rest_framework import status
from base.permissions import UserPermission
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.models import Token
from .serializers import LoginSerializer
from django.contrib.auth import authenticate
# Create your views here.


class UserInfoView(HandleException, APIView):
    permission_classes=[UserPermission]
    def get(self,request):
        user=User.objects.all()
        serializer=UserInfoSerializer(user,many=True)
        return Response(
           {"status": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
    def post(self, request):
        data=request.data
        serializer=UserInfoSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save(password=make_password(data["password"]))
        return Response(
                {"status": True, "message": "Data saved successfully"},
                status=status.HTTP_201_CREATED,
            )
    def patch(self, request):
        user=request.user     
        serializer = UserInfoSerializer(user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"status": True, "message": "Data updated successfully"}, status=status.HTTP_200_OK)
        return Response({"status": False, "message": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)
    
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

class LoginView(APIView):
    def post(self,request):
        serializer=LoginSerializer(data=request.data)
        if serializer.is_valid():
            email=serializer.validated_data["email"]
            password=serializer.validated_data["password"]
            user=authenticate(email=email,password=password)
            if user:
                token,created=Token.objects.get_or_create(user=user)
                return Response({'token':token.key},status=status.HTTP_200_OK)
            else:
                return Response({"error":"Invalid Credentials"},status=status.HTTP_401_UNAUTHORIZED)
        return Response({"status":False,"message":"Invalid Data"},status=status.HTTP_400_BAD_REQUEST)

