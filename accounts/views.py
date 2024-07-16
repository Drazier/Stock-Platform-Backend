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
from .alert import return_df, alert_rsi, alert_macd, alert_adx, alert_bb, alert_ema, alert_sma, send_email, cal_rsi, cal_macd, cal_adx, cal_bb, cal_ema, cal_sma
# Create your views here.


class UserInfoView(HandleException, APIView):
    permission_classes=[UserPermission]
    def get(self, request):
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
        user = request.data.get('user')
        strategy = request.data.get('strategy_name')
        if not user or not strategy:
            return Response({"status": False, "message": "User and strategy_name are required"},status=status.HTTP_400_BAD_REQUEST)
        try:
            Strategy.objects.get(user=user, strategy_name=strategy)
            return Response({"status": False, "message": "Strategy already exists for this user"},status=status.HTTP_400_BAD_REQUEST)
        except Strategy.DoesNotExist:
            serializer = StrategySerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({"status": True, "message": "Data saved successfully"},status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        user = request.data.get('user')
        strategy=request.data.get('strategy_name')
        try:
            strategy_instance = Strategy.objects.get(user=user,strategy_name=strategy)
        except Strategy.DoesNotExist:
            return Response({"status": False, "message": "Strategy not found"},status=status.HTTP_404_NOT_FOUND)
        serializer = StrategySerializer(strategy_instance, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response({"status": True, "message": "Data updated successfully"}, status=status.HTTP_200_OK)
        return Response({"status": False, "message": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.data.get('user')
        strategy=request.data.get('strategy_name')
        deleted=Strategy.objects.filter(user=user,strategy_name=strategy).delete()
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
            
                return Response({'token':token.key,"message":"Login Successful!"},status=status.HTTP_200_OK)
            else:
                return Response({"error":"Invalid Credentials"},status=status.HTTP_401_UNAUTHORIZED)
        return Response({"status":False,"message":"Invalid Data"},status=status.HTTP_400_BAD_REQUEST)

class FetchDataView(APIView):
    def get(self, request):
        ticker = request.query_params.get("ticker")
        print(ticker)
        ticker = TickerSymbol.objects.get(ticker=ticker).ticker
        if not ticker:
            return Response({"status": False, "message": "Ticker is required"},
                status=status.HTTP_400_BAD_REQUEST,)
        response = fetch_data(ticker)
        return Response({"status": True, "data": response}, status=status.HTTP_200_OK)

#this api is currently sending alerts on default parameters
#it takes user, strategy_name, para_1 as compulsory inputs but only uses the user parameter for filtration. the rest 2 are compulsory because acc to Strategy model those 2 cannot be left blank  
class StrategyAlertView(APIView):
    def post(self, request):
        serializer = StrategySerializer(data=request.data)
        print(request.data)
        if serializer.is_valid(raise_exception=True):
            stock="AXISBANK"
            sql_df=return_df(stock)
            user = serializer.validated_data.get('user')
            try:
                strategy = Strategy.objects.filter(user=user)
            except Strategy.DoesNotExist:
                return Response({"status": False, "message": "No such user exists"},status=status.HTTP_400_BAD_REQUEST)
            strategy_list=list(strategy.values_list("strategy_name", flat=True))
            # print("------------------------")
            # print(strategy)
            # print("-------------------------")
            if strategy_list:
                message=f"*{stock} Indicators Update*"
                alert=""
                if 'rsi' in strategy_list:
                    message+="\n"+alert_rsi(data=sql_df)
                    alert=alert+"RSI "
                if "adx" in strategy_list:
                    message+="\n"+alert_adx(data=sql_df)
                    alert+="ADX "
                if "ema" in strategy_list:
                    message+="\n"+alert_ema(data=sql_df)
                    alert+="EMA "
                if "sma" in strategy_list:
                    message+="\n"+alert_sma(data=sql_df)
                    alert+="SMA "
                if "macd" in strategy_list:
                    message+="\n"+alert_macd(data=sql_df)
                    alert+="MACD "
                if "bb" in strategy_list:
                    message+="\n"+alert_bb(data=sql_df)
                    alert+="BB "
                
                send_email(message_text=message)
                print(message)
                return Response({"message": f"{alert}strategy executed", "data": strategy_list}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No strategy executed", "data":strategy_list}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#rsi api currently not working
class RsiView(APIView):
    def post(self, request):
        serializer = StrategySerializer(data=request.data)
        print(request.data)
        if serializer.is_valid(raise_exception=True):
            stock="AXISBANK"
            df=return_df(stock)
            # data=[]
            user = serializer.validated_data.get('user')
            try:
                strategy = Strategy.objects.filter(user=user,strategy_name='rsi')
            except Strategy.DoesNotExist:
                return Response({"status": False, "message": "No such strategy exists"},status=status.HTTP_400_BAD_REQUEST)
            para_1 = strategy.para_1
            if not para_1:
                para_1=14
            rsi_df=cal_rsi(df,"15m",para_1)
            rsi_dict=rsi_df.to_dict(orient='records')
            # data.append(rsi_dict)
            print(rsi_dict)
            return Response({"message": f"{stock} RSI data sent", "data": rsi_dict}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)