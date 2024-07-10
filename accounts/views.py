from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import User, Strategy, TickerSymbol
from .serializers import UserInfoSerializer, StrategySerializer
from base.views import HandleException
from rest_framework import status
from base.permissions import UserPermission
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.models import Token
from .serializers import LoginSerializer
from django.contrib.auth import authenticate
from utils.data_fetch import fetch_data
# Create your views here.


class UserInfoView(HandleException, APIView):
    permission_classes=[UserPermission]
    def get(self,request):
        user=User.objects.all()
        serializer=UserInfoSerializer(user,many=True)
        return Response({"status": True, "data": serializer.data}, status=status.HTTP_200_OK)
    
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
        user = request.data.get('username')  
        try:
            user_instance = User.objects.get(username=user)
        except User.DoesNotExist:
            return Response({"status": False, "message": "User not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = UserInfoSerializer(user_instance, data=request.data, partial=True)
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
        serializer = StrategySerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            Strategy.objects.create(**serializer.validated_data)
            return Response(
                {"status": True, "message": "Data saved successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        user = request.data.get('user')
        try:
            strategy_instance = Strategy.objects.get(user=user)
        except Strategy.DoesNotExist:
            return Response({"status": False, "message": "Strategy not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = StrategySerializer(strategy_instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"status": True, "message": "Data updated successfully"}, status=status.HTTP_200_OK)
        return Response({"status": False, "message": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.data.get('user')
        deleted=Strategy.objects.filter(user=user).delete()
        if deleted:
            return Response(
                {"status": True, "message": "Data deleted successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"status": False, "message": "Strategy not found"},
            status=status.HTTP_404_NOT_FOUND,
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

class FetchDataView(APIView):

    def get(self, request):
        data = request.data
        ticker = data.get("ticker", None)
        ticker = TickerSymbol.objects.get(uuid=ticker).ticker
        if not ticker:
            return Response(
                {"status": False, "message": "Ticker is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        response = fetch_data(ticker)
        return Response({"status": True, "data": response}, status=status.HTTP_200_OK)

