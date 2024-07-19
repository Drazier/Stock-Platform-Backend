from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import User, Strategy, TickerSymbol
from .serializers import UserInfoSerializer, StrategySerializer, LoginSerializer, IndicatorSerializer
from base.views import HandleException
from rest_framework import status
from base.permissions import UserPermission
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from utils.data_fetch import fetch_data
from .alert import *
# Create your views here.


class UserInfoView(HandleException, APIView):
    permission_classes=[UserPermission]
    def get(self, request):
        email = request.query_params.get("email")
        if not email:
            return Response({"status": False, "message": "Email is required"},status=status.HTTP_400_BAD_REQUEST,)
        user=User.objects.get(email=email)
        user=UserInfoSerializer(user)
        return Response({"status": True, "data": user.data}, status=status.HTTP_200_OK)
    
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
        deleted=Strategy.objects.get(user=user,strategy_name=strategy).delete()
        if deleted:
            return Response(
                {"status": True, "message": "Data deleted successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"status": False, "message": "Strategy not found"}, status=status.HTTP_404_NOT_FOUND,)

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
        serializer = IndicatorSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid(raise_exception=True):
            stock=serializer.validated_data.get('ticker')
            try:
                TickerSymbol.objects.get(ticker=stock)
            except TickerSymbol.DoesNotExist:
                return Response({"status": False, "message": "No such ticker exists"},status=status.HTTP_400_BAD_REQUEST)
            user = serializer.validated_data.get('user')
            sql_df=return_df(stock)
            try:
                strategy = Strategy.objects.filter(user=user)
            except Strategy.DoesNotExist:
                return Response({"status": False, "message": "No such user exists"},status=status.HTTP_400_BAD_REQUEST)
            strategy_list=list(strategy.values_list("strategy_name", flat=True))
            print("-------------------------")
            print("-------------------------")
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
                if "kc" in strategy_list:
                    message+="\n"+alert_kc(data=sql_df)
                    alert+="KC "

                if message=="":
                    return Response({"message": "No alert for now!", "data": strategy_list}, status=status.HTTP_200_OK)
                else:
                    send_email(message_text=message)
                    send_telegram_message(message)
                    print(message)
                    return Response({"message": f"{alert}strategy executed", "data": strategy_list}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No strategy executed", "data":strategy_list}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class Rsi(APIView):
    def post(self, request):
        serializer = IndicatorSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid(raise_exception=True):
            stock=serializer.validated_data.get('ticker')
            try:
                TickerSymbol.objects.get(ticker=stock)
            except TickerSymbol.DoesNotExist:
                return Response({"status": False, "message": "No such ticker exists"},status=status.HTTP_400_BAD_REQUEST)
            user = serializer.validated_data.get('user')
            df=return_df(stock)
            data=[]
            try:
                strategy = Strategy.objects.get(user=user, strategy_name='rsi')
            except Strategy.DoesNotExist:
                return Response({"status": False, "message": "No such strategy exists"},status=status.HTTP_400_BAD_REQUEST)
            para_1 = strategy.para_1 if strategy.para_1 is not None else 14
            
            for time in ["15m","60m","1d"]:
                if time=="60m":
                    df=df.loc[df['Datetime'].dt.minute==15]
                elif time=="1d":
                    df=df.loc[df['Datetime'].dt.hour==9]
                rsi_df=cal_rsi(df,time,para_1)
                rsi_dict=rsi_df.to_dict(orient='records')
                data.append(rsi_dict)
            
            return Response({"message": f"{stock} RSI data sent", "data": data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class Adx(APIView):
    def post(self, request):
        serializer = IndicatorSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid(raise_exception=True):
            stock=serializer.validated_data.get('ticker')
            try:
                TickerSymbol.objects.get(ticker=stock)
            except TickerSymbol.DoesNotExist:
                return Response({"status": False, "message": "No such ticker exists"},status=status.HTTP_400_BAD_REQUEST)
            user = serializer.validated_data.get('user')
            df=return_df(stock)
            data=[]
            try:
                strategy = Strategy.objects.get(user=user, strategy_name='adx')
            except Strategy.DoesNotExist:
                return Response({"status": False, "message": "No such strategy exists"},status=status.HTTP_400_BAD_REQUEST)
            para_1 = strategy.para_1 if strategy.para_1 is not None else 14
            
            for time in ["15m","60m","1d"]:
                if time=="60m":
                    df=df.loc[df['Datetime'].dt.minute==15]
                elif time=="1d":
                    df=df.loc[df['Datetime'].dt.hour==9]
                rsi_df=cal_adx(df,time,para_1)
                rsi_dict=rsi_df.to_dict(orient='records')
                # print(rsi_df.tail(10))
                # print((rsi_df.tail(5)).to_dict(orient='records'))
                data.append(rsi_dict)
            
            return Response({"message": f"{stock} ADX data sent", "data": data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class Macd(APIView):
    def post(self, request):
        serializer = IndicatorSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid(raise_exception=True):
            stock=serializer.validated_data.get('ticker')
            try:
                TickerSymbol.objects.get(ticker=stock)
            except TickerSymbol.DoesNotExist:
                return Response({"status": False, "message": "No such ticker exists"},status=status.HTTP_400_BAD_REQUEST)
            user = serializer.validated_data.get('user')
            df=return_df(stock)
            data=[]
            try:
                strategy = Strategy.objects.get(user=user, strategy_name='macd')
            except Strategy.DoesNotExist:
                return Response({"status": False, "message": "No such strategy exists"},status=status.HTTP_400_BAD_REQUEST)
            para_1 = strategy.para_1 if strategy.para_1 is not None else 12
            para_2 = strategy.para_2 if strategy.para_2 is not None else 26
            para_3 = strategy.para_3 if strategy.para_3 is not None else 9
            for time in ["15m","60m","1d"]:
                if time=="60m":
                    df=df.loc[df['Datetime'].dt.minute==15]
                elif time=="1d":
                    df=df.loc[df['Datetime'].dt.hour==9]
                rsi_df=cal_macd(df,time,para_1,para_2,para_3)
                rsi_dict=rsi_df.to_dict(orient='records')
                data.append(rsi_dict)
            
            return Response({"message": f"{stock} MACD data sent", "data": data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class BB(APIView):
    def post(self, request):
        serializer = IndicatorSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid(raise_exception=True):
            stock=serializer.validated_data.get('ticker')
            try:
                TickerSymbol.objects.get(ticker=stock)
            except TickerSymbol.DoesNotExist:
                return Response({"status": False, "message": "No such ticker exists"},status=status.HTTP_400_BAD_REQUEST)
            user = serializer.validated_data.get('user')
            df=return_df(stock)
            data=[]
            try:
                strategy = Strategy.objects.get(user=user, strategy_name='bb')
            except Strategy.DoesNotExist:
                return Response({"status": False, "message": "No such strategy exists"},status=status.HTTP_400_BAD_REQUEST)
            para_1 = strategy.para_1 if strategy.para_1 is not None else 20
            for time in ["15m","60m","1d"]:
                if time=="60m":
                    df=df.loc[df['Datetime'].dt.minute==15]
                elif time=="1d":
                    df=df.loc[df['Datetime'].dt.hour==9]
                rsi_df=cal_bb(df,time,para_1)
                rsi_dict=rsi_df.to_dict(orient='records')
                data.append(rsi_dict)
            
            return Response({"message": f"{stock} BB data sent", "data": data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class Ema(APIView):
    def post(self, request):
        serializer = IndicatorSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid(raise_exception=True):
            stock=serializer.validated_data.get('ticker')
            try:
                TickerSymbol.objects.get(ticker=stock)
            except TickerSymbol.DoesNotExist:
                return Response({"status": False, "message": "No such ticker exists"},status=status.HTTP_400_BAD_REQUEST)
            user = serializer.validated_data.get('user')
            df=return_df(stock)
            data=[]
            try:
                strategy = Strategy.objects.get(user=user, strategy_name='ema')
            except Strategy.DoesNotExist:
                return Response({"status": False, "message": "No such strategy exists"},status=status.HTTP_400_BAD_REQUEST)
            para_1 = strategy.para_1 if strategy.para_1 is not None else 20
            para_2 = strategy.para_2 if strategy.para_2 is not None else 50
            para_3 = strategy.para_3 if strategy.para_3 is not None else 100
            para_4 = strategy.para_4 if strategy.para_4 is not None else 200
            for time in ["15m","60m","1d"]:
                if time=="60m":
                    df=df.loc[df['Datetime'].dt.minute==15]
                elif time=="1d":
                    df=df.loc[df['Datetime'].dt.hour==9]
                rsi_df=cal_ema(df,time,para_1,para_2,para_3,para_4)
                print(rsi_df.tail(10))
                rsi_dict=rsi_df.to_dict(orient='records')
                data.append(rsi_dict)
            
            return Response({"message": f"{stock} EMA data sent", "data": data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class Sma(APIView):
    def post(self, request):
        serializer = IndicatorSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid(raise_exception=True):
            stock=serializer.validated_data.get('ticker')
            try:
                TickerSymbol.objects.get(ticker=stock)
            except TickerSymbol.DoesNotExist:
                return Response({"status": False, "message": "No such ticker exists"},status=status.HTTP_400_BAD_REQUEST)
            user = serializer.validated_data.get('user')
            df=return_df(stock)
            data=[]
            try:
                strategy = Strategy.objects.get(user=user, strategy_name='sma')
            except Strategy.DoesNotExist:
                return Response({"status": False, "message": "No such strategy exists"},status=status.HTTP_400_BAD_REQUEST)
            para_1 = strategy.para_1 if strategy.para_1 is not None else 20
            para_2 = strategy.para_2 if strategy.para_2 is not None else 50
            para_3 = strategy.para_3 if strategy.para_3 is not None else 100
            para_4 = strategy.para_4 if strategy.para_4 is not None else 200
            for time in ["15m","60m","1d"]:
                if time=="60m":
                    df=df.loc[df['Datetime'].dt.minute==15]
                elif time=="1d":
                    df=df.loc[df['Datetime'].dt.hour==9]
                rsi_df=cal_sma(df,time,para_1,para_2,para_3,para_4)
                print(rsi_df.tail(10))
                rsi_dict=rsi_df.to_dict(orient='records')
                data.append(rsi_dict)
            
            return Response({"message": f"{stock} SMA data sent", "data": data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class KC(APIView):
    def post(self, request):
        serializer = IndicatorSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid(raise_exception=True):
            stock=serializer.validated_data.get('ticker')
            try:
                TickerSymbol.objects.get(ticker=stock)
            except TickerSymbol.DoesNotExist:
                return Response({"status": False, "message": "No such ticker exists"},status=status.HTTP_400_BAD_REQUEST)
            user = serializer.validated_data.get('user')
            df=return_df(stock)
            data=[]
            try:
                strategy = Strategy.objects.get(user=user, strategy_name='kc')
            except Strategy.DoesNotExist:
                return Response({"status": False, "message": "No such strategy exists"},status=status.HTTP_400_BAD_REQUEST)
            para_1 = strategy.para_1 if strategy.para_1 is not None else 20
            
            for time in ["15m","60m","1d"]:
                if time=="60m":
                    df=df.loc[df['Datetime'].dt.minute==15]
                elif time=="1d":
                    df=df.loc[df['Datetime'].dt.hour==9]
                rsi_df=cal_kc(df,time,para_1)
                rsi_dict=rsi_df.to_dict(orient='records')
                data.append(rsi_dict)
            
            return Response({"message": f"{stock} KC data sent", "data": data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)