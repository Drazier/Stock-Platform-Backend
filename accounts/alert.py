from warnings import filterwarnings
filterwarnings('ignore')
# Import necessary libraries
import yfinance as yf  # Library to fetch stock data from Yahoo Finance
import pandas as pd  # Library for data manipulation and analysis
import numpy as np  # Library for numerical computing
# import plotly.graph_objs as go  # Library for interactive plotting
import smtplib  # Library for sending email
from email.mime.text import MIMEText  # MIMEText to create email body
from email.mime.multipart import MIMEMultipart  # MIMEMultipart to create email message
from datetime import datetime  # Library for datetime operations
import time  # Library for time-related operations
from IPython.display import clear_output, display  # Library for clearing output and displaying output
import subprocess  # Library for subprocess management
import re  # Library for regular expressions
import pyautogui  # Library for GUI automation
from telegram import Bot
from telegram.error import TelegramError

# from plotly.subplots import make_subplots

from sqlalchemy import create_engine, Table, MetaData  # Library for database connection

def send_telegram_message(message, api_token="7394095348:AAFiJ8WcVU25mQkDcaYjtmffWUNhKVFUyFQ", chat_id=""):
    """
    Sends a message to a specified chat ID using a Telegram bot.
    
    :param api_token: The API token of the Telegram bot.
    :param chat_id: The chat ID or username to send the message to.
    :param message: The message to send.
    :return: True if the message is sent successfully, False otherwise.
    """
    bot = Bot(token=api_token)
    
    try:
        bot.send_message(chat_id=chat_id, text=message)
        return True
    except TelegramError as e:
        print(f"Error sending message: {e}")
        return False

def return_df(stock):
    user_name = "postgres"
    user_password = "root"
    host = "localhost"
    port = "5432"
    database_name = "Demo"

    # PostgreSQL connection string
    postgres_connection_string = f"postgresql://{user_name}:{user_password}@{host}:{port}/{database_name}"

    # Create the connection to the database
    engine = create_engine(postgres_connection_string)
    sql_df=pd.read_sql_table(stock, engine)
    return sql_df

# Function to send email messages

def send_email(message_text):
    """
    Function to send email messages.

    Parameters:
    - message_text: Text message to be sent via email.

    The function sets up email parameters, creates a MIME multipart message,
    and sends the email using the smtplib library to the specified recipient.
    """

    # Set up email parameters
    sender_email = "kaushal.cilans@gmail.com"  # Email address of the sender
    receiver_email = "harshilc.intern@gmail.com"  # Email address of the receiver
    password = "fndkdayybiqfotsy"  # Password of the sender's email account

    subject = "EMA Crossover Alert"  # Subject of the email
    body = message_text  # Body of the email, contains the message text

    # Create message
    message = MIMEMultipart()  # Create a MIME multipart message
    message["From"] = sender_email  # Set the 'From' field of the email
    message["To"] = receiver_email  # Set the 'To' field of the email
    message["Subject"] = subject  # Set the subject of the email
    message.attach(MIMEText(body, "plain"))  # Attach the body of the email as plain text

    # Print Statement Before Sending Email
    print("Sending Email...")  # Print statement to indicate email sending process is initiated

    # Establish a connection with the SMTP server
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:  # Connect to Gmail SMTP server
            server.starttls()  # Start TLS encryption
            server.login(sender_email, password)  # Login to the email account
            server.sendmail(sender_email, receiver_email, message.as_string())  # Send the email message
        print("Email Sent Successfully!")  # Print statement if email is sent successfully
    except Exception as e:
        print("Error Sending Email:", str(e))  # Print statement if an error occurs while sending the email


# Function to send WhatsApp messages to numbers listed in a CSV file

def send_whatsapp_messages(numbers_filename, message_text):
    """
    Function to send WhatsApp messages to numbers listed in a CSV file.

    Parameters:
    - numbers_filename: Path to the CSV file containing contact numbers.
    - message_text: Text message to be sent via WhatsApp.

    The function reads the contact numbers from the provided CSV file, validates each number,
    and sends the specified message via WhatsApp using subprocess and pyautogui libraries.
    """

    # Display the selected contact file path
    print("\n========================= Selected Contact File Path ===========================\n")
    print(numbers_filename)

    # Read the CSV file containing contact numbers into a DataFrame
    df1 = pd.read_csv(numbers_filename)
    print(df1)

    # Process the input text message
    input_txt = message_text

    # List to store rejected numbers
    rejected_number = []

    # Iterate through each row in the DataFrame
    for _, i in df1.iterrows():
        print(i['Number'])
        print(i['Name'])

        # Check if the number matches the valid pattern
        r = re.fullmatch('[6-9][0-9]{9}', str(i['Number']))
        if r is not None:
            print('Valid Number')

            raw_text = "Hello there, *{name}* !".format(name=i['Name'])+message_text
            input_txt = raw_text.replace(" ", "%20")
            input_txt = input_txt.replace(' ', '%20')
            input_txt = input_txt.replace('\n', '%0A')
            input_txt = input_txt.replace(':)', '\U0001F601')

            print(input_txt)

            try:
                print('Opening WhatsApp...')
                subprocess.Popen(["cmd", "/C", "start whatsapp://"], shell=True)
                time.sleep(2)
                subprocess.Popen(["cmd", "/C", "start whatsapp://send?phone=" + str(i['Number'])], shell=True)
                time.sleep(2)
                subprocess.Popen(["cmd", "/C", "start whatsapp://send?phone=" + str(i['Number']) + "^&text=" + input_txt], shell=True)
                time.sleep(2)
                print('WhatsApp Opened')
                pyautogui.click(1500,695)
                pyautogui.press('enter')  # Press Enter key to send message
                print('Message Sent')

            except Exception as e:
                print(e)

        else:
            print('Not a valid number')
            rejected_number.append(str(i['Number']))



    # Print the list of rejected numbers
    print(rejected_number)

    # Create a DataFrame for rejected numbers and store them in a CSV file
    rejected_num = pd.DataFrame()
    for i in rejected_number:
        print(i)
        rejected = df1.loc[df1['Number'] == i]
        rejected_num = pd.concat([rejected_num, rejected])
        print(rejected_num)

    rejected_num.to_csv('rejected_numbers.csv')


# Initialize figure
# fig = go.Figure()


def initial_fetch_data(symbol, date, conn):
    date = datetime.strptime(date, "%Y-%m-%d")
    # temp_end = datetime.strptime("2024-06-01", "%Y-%m-%d")

    # Download 15-minute data
    min15 = yf.download(symbol, start=date, interval="15m")
    min15.index = min15.index.strftime("%Y-%m-%d %H:%M:%S")
    min15.index = pd.to_datetime(min15.index)
    min15["Date"] = min15.index.date
    for i in range(len(min15.columns)):
        min15.columns.values[i] = "15m_" + min15.columns.values[i]
    min15.rename(columns={"15m_Date": "Date"}, inplace=True)
    min15 = min15.reindex(
        columns=[
            "Date",
            "15m_Open",
            "15m_High",
            "15m_Low",
            "15m_Close",
            "15m_Adj Close",
            "15m_Volume",
        ]
    )
    # min15 = min15.resample("15min").ffill()

    # Download 60-minute data
    min60 = yf.download(symbol, start=date, interval="60m")
    min60.index = min60.index.strftime("%Y-%m-%d %H:%M:%S")
    min60.index = pd.to_datetime(min60.index)
    min60["Date"] = min60.index.date
    for i in range(len(min60.columns)):
        min60.columns.values[i] = "60m_" + min60.columns.values[i]
    min60.rename(columns={"60m_Date": "Date"}, inplace=True)
    min60 = min60.reindex(
        columns=[
            "Date",
            "60m_Open",
            "60m_High",
            "60m_Low",
            "60m_Close",
            "60m_Adj Close",
            "60m_Volume",
        ]
    )
    min60 = min60.resample("15min").ffill()

    # Download 1-day data
    day1 = yf.download(symbol, start=date, interval="1d")
    day1.index = day1.index.strftime("%Y-%m-%d")
    day1.index = pd.to_datetime(day1.index)
    day1["Date"] = day1.index.date
    for i in range(len(day1.columns)):
        day1.columns.values[i] = "1d_" + day1.columns.values[i]
    day1.rename(columns={"1d_Date": "Date"}, inplace=True)
    day1 = day1.reindex(
        columns=[
            "Date",
            "1d_Open",
            "1d_High",
            "1d_Low",
            "1d_Close",
            "1d_Adj Close",
            "1d_Volume",
        ]
    )
    day1 = day1.resample("15min").ffill()

    # Concatenate dataframes
    main_df = pd.concat([min15, min60, day1], axis=1)
    # Drop duplicate columns
    main_df = main_df.loc[:, ~main_df.columns.duplicated()]
    # pd.set_option('display.max_rows', None)
    main_df = main_df.dropna(subset=["15m_Open", "15m_High", "15m_Low", "15m_Close"])

    return main_df

def cal_rsi(df,time,period=14):
    df['Change']=df[f'{time}_Close']-df[f'{time}_Close'].shift(1)
    df['Gain']=np.where(df['Change']>0,df['Change'], 0)
    df['Loss']=np.where(df['Change']<0,-df['Change'], 0)
    df['Avg_Gain'] = df['Gain'].rolling(window=period).mean()
    df['Avg_Loss'] = df['Loss'].rolling(window=period).mean()
    df['RS'] = df['Avg_Gain']/df['Avg_Loss']
    df[f'RSI_{time}'] = 100 - (100 / (1 + df['RS']))
    return df[['Datetime',f'RSI_{time}']]

def check_rsi(df,time):
    cur=df[f"RSI_{time}"].iloc[-1]
    prev=df[f"RSI_{time}"].iloc[-2]
    # print(cur)
    # print(prev)
    if(cur>70 and prev<=70):
        return("RSI crosses above")
    if(cur<30 and prev>=30):
        return("RSI crosses below")
    return("No update")

def alert_rsi(data, period=14):
    message = "\nRSI update : "

    data_15=data.tail(period+2)
    # print("1 : \n",data_15["15m_Close"])
    data_15=cal_rsi(data_15,"15m",period)
    message+="\n15 minute "+check_rsi(data_15,"15m")

    filt=(data['Datetime'].dt.minute==15)
    data=data.loc[filt]
    data_60=data.tail(period+2)
    # print("2 :\n",data_60["60m_Close"])
    data_60=cal_rsi(data_60,"60m",period)
    message+="\n60 minute "+check_rsi(data_60,"60m")

    filt = (data['Datetime'].dt.hour == 9)
    data_1=data.loc[filt].tail(period+2)
    # print("3 :\n",data_1["1d_Close"])
    data_1=cal_rsi(data_1,"1d",period)
    message+="\nDaily "+check_rsi(data_1,"1d")
    
    if message=="\nRSI update : ":
        message="\nNo RSI update!"
    
    # send_whatsapp_messages("leads.csv", message)
    # send_email(message_text=message)
    # send_telegram_message(message)
    return(message)

stock="HDFCBANK"
# print(stock)

def cal_macd(df,time,para1=12,para2=26,para3=9):
    df['EMA_12'] = df[f'{time}_Close'].ewm(span=para1, adjust=False).mean()
    df['EMA_26'] = df[f'{time}_Close'].ewm(span=para2, adjust=False).mean()
    df[f'MACD_{time}']=df['EMA_12']-df['EMA_26']
    df[f'MACD_signal_{time}'] = df[f'MACD_{time}'].ewm(span=para3, adjust=False).mean()
    return df[['Datetime',f'MACD_{time}',f'MACD_signal_{time}']]

def check_macd(df,time):
    df.rename(columns={f'MACD_{time}': 'MACD', f'MACD_signal_{time}': 'MACD_signal'}, inplace=True)
    pre_macd=df['MACD'].iloc[-2]
    pre_macd_signal=df['MACD_signal'].iloc[-2]
    cur_macd=df['MACD'].iloc[-1]
    cur_macd_signal=df['MACD_signal'].iloc[-1]
    message="No update"
    # print(cur_macd)
    # print(cur_macd_signal)
    # print(pre_macd)
    # print(pre_macd_signal)
    if cur_macd>cur_macd_signal and pre_macd<pre_macd_signal:
        message="MACD crosses above"
    if cur_macd<cur_macd_signal and pre_macd>pre_macd_signal:
        message="MACD crosses below"
    return message

def alert_macd(data,para1=12,para2=26,para3=9):
    df_15m=data.tail(para2+2)
    # print(df_15m["15m_Close"])
    message="\nMACD update : "
    df_15m=cal_macd(df_15m,"15m",para1,para2,para3)
    message=message+"\n15 minute "+check_macd(df_15m,"15m")
    
    filt=(data['Datetime'].dt.minute==15)
    data=data.loc[filt]
    df_60m=data.tail(para2+2)
    # print(df_60m["60m_Close"])
    df_60m=cal_macd(df_60m,"60m",para1,para2,para3)
    message=message+"\n60 minute "+check_macd(df_60m,"60m")
    
    filt=(data['Datetime'].dt.hour==9)
    df_1d=data.loc[filt].tail(para2+2)
    # print(df_1d["1d_Close"])
    cal_macd(df_1d,"1d",para1,para2,para3)
    message=message+"\nDaily "+check_macd(df_1d,"1d")
    
    # send_whatsapp_messages("leads.csv", message)
    # send_email(message_text=message)
    return(message)

def cal_dm(df,n):
    up_move = df["High"] - df["High"].shift(1)
    down_move = df["Low"].shift(1) - df["Low"]
    df['+DM'] = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
    df['-DM'] = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
    df['+DM_smooth'] = df["+DM"].ewm(span=n, adjust=False).mean()
    df['-DM_smooth'] = df["-DM"].ewm(span=n, adjust=False).mean()
    df.drop(columns=["+DM","-DM"], inplace=True)#
    df = cal_index(df,n)
    return df

def cal_tr(df, n):
    df['TR'] = np.maximum(df["High"] - df["Low"], 
                      np.maximum(abs(df["High"] - df["Close"].shift(1)), 
                                 abs(df["Low"] - df["Close"].shift(1))))
    df['ATR'] = df["TR"].ewm(span=n, adjust=False).mean()
    del df['TR']#
    df = cal_dm(df,n)
    return df

def cal_index(df,n):
    df['+DI'] = (df['+DM_smooth'] / df['ATR']) * 100
    df['-DI'] = (df['-DM_smooth'] / df['ATR']) * 100
    df['DX'] = abs(df['+DI'] - df['-DI']) / (df['+DI'] + df['-DI']) * 100
    
    df['ADX'] = df['DX'].rolling(window=n).mean()
    df.drop(columns=['ATR','+DM_smooth', '-DM_smooth', 'DX'], inplace=True)#
    return df


def cal_adx(df, time, n):
    df = df[[f'{time}_High', f'{time}_Low', f'{time}_Close']].apply(pd.to_numeric, errors='coerce')
    df.rename(columns={f'{time}_High': 'High', f'{time}_Low': 'Low', f'{time}_Close':'Close'}, inplace=True)
    df = cal_tr(df, n)
    df.rename(columns={'ADX':f'ADX_{time}','+DI':f'+DI_{time}','-DI':f'-DI_{time}'},inplace=True)
    return df[['Datetime',f'ADX_{time}',f'+DI_{time}',f'-DI_{time}']]


def check_adx(df,time):
    df.rename(columns={f'ADX_{time}':'ADX',f'+DI_{time}':'+DI',f'-DI_{time}':'-DI'},inplace=True)
    cur_adx = df['ADX'].iloc[-1]
    pre_pdi = df['+DI'].iloc[-2]
    cur_pdi = df['+DI'].iloc[-1]
    pre_mdi = df['-DI'].iloc[-2]
    cur_mdi = df['-DI'].iloc[-1]
    df.drop(columns=['+DI', '-DI', 'ADX'], inplace=True)

    # print("-----------------")
    # print(cur_adx)
    # print(pre_pdi)
    # print(cur_pdi)
    # print(pre_mdi)
    # print(cur_mdi)

    if cur_adx > 25:
        if cur_pdi > cur_mdi and pre_pdi <= pre_mdi:
            return "ADX signals uptrend"
        if cur_pdi < cur_mdi and pre_pdi >= pre_mdi:
            return "ADX signals downtrend"    
    return "No Update"

def alert_adx(data, period=14):
    message = "\nADX update : "
    
    data_15 = data.tail(2 * period + 2)
    data_15=cal_adx(data_15, '15m', n=period)
    message += "\n15 minute "+check_adx(data_15, '15m')
    
    filt_60 = (data['Datetime'].dt.minute == 15)
    data=data.loc[filt_60]
    data_60 = data.tail(2 * period + 2)
    data_60=cal_adx(data_60, '60m', n=period)
    message += "\n60 minute "+check_adx(data_60, '60m')
    
    
    filt_daily = (data['Datetime'].dt.hour == 9)
    data_daily = data.loc[filt_daily].tail(2 * period + 2)
    data_daily=cal_adx(data_daily, '1d', n=period)
    message += "\nDaily "+check_adx(data_daily, '1d')
    
    if message == "\nADX update : ":
        message = "\nNo ADX update!"
    
    # send_whatsapp_messages("leads.csv", message)
    # send_email(message_text=message)
    return(message)

def cal_bb(df,time,n):
    df.rename(columns={f'{time}_Close':'Close'})
    df['SMA_20'] = df[f'Close'].rolling(window=n).mean()
    df['SD_20'] = df['Close'].rolling(window=n).std()
    df['BB_up'] = df['SMA_20']+2*df['SD_20']
    df['BB_low'] = df['SMA_20']-2*df['SD_20']
    df.rename(columns={'SMA_20':f'SMA_20_{time}','BB_up':f'BB_up_{time}', 'BB_low':f'BB_low_{time}'},inplace=True)
    return df[['Datetime',f'SMA_20_{time}',f'BB_up_{time}',f'BB_low_{time}']]

def check_bb(df,time):
    df.rename(columns={f'SMA_20_{time}':'SMA_20',f'BB_up_{time}':'BB_up', f'BB_low_{time}':'BB_low'},inplace=True)
    cur=df['Close'].iloc[-1]
    cur_bb_up=df['BB_up'].iloc[-1]
    cur_bb_low=df['BB_low'].iloc[-1]
    # print("--------------")
    # print(cur)
    # print(cur_bb_low)
    # print(cur_bb_up)
    df.drop(columns=['SMA_20', 'BB_up', 'BB_low'], inplace=True)
    if(cur>cur_bb_up):
        return("Price crosses Upper band")
    if(cur<cur_bb_low):
        return("Price crosses Lower band")
    return("No update")

def alert_bb(data,n=20):
    message = "\nBB update : "
    
    data_15 = data.tail(n + 2)
    data_15=cal_bb(data_15, '15m', n)
    message += "\n15 minute "+check_bb(data_15, '15m')
    
    filt_60 = (data['Datetime'].dt.minute == 15)
    data=data.loc[filt_60]
    data_60 = data.tail(n + 2)
    data_60=cal_bb(data_60, '60m', n)
    message += "\n60 minute "+check_bb(data_60, '60m')
    
    filt_daily = (data['Datetime'].dt.hour == 9)
    data_daily = data.loc[filt_daily].tail(n +2)
    data_daily=cal_bb(data_daily, '1d', n)
    message += f"\nDaily "+check_bb(data_daily, '1d')
    
    if message == "\BB update : ":
        message = "\nNo BB update!"
    
    # send_whatsapp_messages("leads.csv", message)
    # send_email(message_text=message)
    return(message)

def cal_ema(data,time,para1=20,para2=50,para3=100,para4=200):
    l=[para1,para2,para3,para4]
    data=data[[f'{time}_Close']]
    data.columns = ['Close']
    periods = [20, 50, 100, 200]
    for i in range(4):
        df=data.tail(l[i]+2)
        print(time," ",l[i]," : \n",df[f'{time}_Close'])
        df[f'{time}_EMA_{periods[i]}'] = df['Close'].ewm(span=l[i], adjust=False).mean()
    return df[['Datetime',f'{time}_EMA_20',f'{time}_EMA_50',f'{time}_EMA_100',f'{time}_EMA_200']]
    
def check_ema(df,time):
    df.rename(columns={f'{time}_EMA_20':'EMA_20', f'{time}_EMA_50':'EMA_50', f'{time}_EMA_100':'EMA_100', f'{time}_EMA_200':'EMA_200'})
    pre_20=df['EMA_20'].iloc[-2]
    cur_20=df['EMA_20'].iloc[-1]
    pre_50=df['EMA_50'].iloc[-2]
    cur_50=df['EMA_50'].iloc[-1]
    pre_100=df['EMA_100'].iloc[-2]
    cur_100=df['EMA_100'].iloc[-1]
    pre_200=df['EMA_200'].iloc[-2]
    cur_200=df['EMA_200'].iloc[-1]
    df.drop(columns=['EMA_20', 'EMA_50', 'EMA_100', 'EMA_200'], inplace=True)
    message=""
    if(pre_20<pre_50 and cur_20>cur_50):
        message+="\n\t20 day EMA crosses above 50 day EMA"
    if(pre_20<pre_100 and cur_20>cur_100):
        message+="\n\t20 day EMA crosses above 100 day EMA"
    if(pre_20<pre_200 and cur_20>cur_200):
        message+="\n\t20 day EMA crosses above 200 day EMA"
    if(pre_50<pre_100 and cur_50>cur_100):
        message+="\n\t50 day EMA crosses above 100 day EMA" 
    if(pre_50<pre_200 and cur_50>cur_200):
        message+="\n\t50 day EMA crosses above 200 day EMA"
    if(pre_100<pre_100 and cur_100>cur_200):
        message+="\n\t100 day EMA crosses above 200 day EMA"
    if(pre_20>pre_50 and cur_20<cur_50):
        message+="\n\t20 day EMA crosses below 50 day EMA"
    if(pre_20>pre_100 and cur_20<cur_100):
        message+="\n\t20 day EMA crosses below 100 day EMA"
    if(pre_20>pre_200 and cur_20<cur_200):
        message+="\n\t20 day EMA crosses below 200 day EMA"
    if(pre_50>pre_100 and cur_50<cur_100):
        message+="\n\t50 day EMA crosses below 100 day EMA" 
    if(pre_50>pre_200 and cur_50<cur_200):
        message+="\n\t50 day EMA crosses below 200 day EMA"
    if(pre_100>pre_100 and cur_100<cur_200):
        message+="\n\t100 day EMA crosses below 200 day EMA"
    if message=="":
        return("No Update!")
    else:
        return(message)

def alert_ema(data,para1=20,para2=50,para3=100,para4=200):
    message = "\nEMA update : "
    
    data_15 = data.tail(para4 + 2)
    data_15=cal_ema(data_15, '15m',para1,para2,para3,para4)
    message += "\n15 minute : *"+check_ema(data_15, '15m')
    
    filt_60 = (data['Datetime'].dt.minute == 15)
    data=data.loc[filt_60]
    data_60 = data.tail(para4+2)
    data_60=cal_ema(data_60, '60m',para1,para2,para3,para4)
    message += "\n*60 minute :* "+check_ema(data_60, '60m')
    
    filt_daily = (data['Datetime'].dt.hour == 9)
    data_daily = data.loc[filt_daily].tail(para4 + 2)
    data_daily=cal_ema(data_daily, '1d',para1,para2,para3,para4)
    message += f"\n*Daily : *"+check_ema(data_daily, '1d')
    
    if message == "\EMA update : ":
        message = "\nNo EMA Update!"
    
    # send_whatsapp_messages("leads.csv", message)
    # send_email(message_text=message)
    return(message)

def cal_sma(data,time,para1=20,para2=50,para3=100,para4=200):
    l=[para1,para2,para3,para4]
    periods = [20, 50, 100, 200]
    for i in range(4):
        df=data.tail(l[i]+2)
        print(time," ",l[i]," : \n",df[f'{time}_Close'])
        df[f'{time}_SMA_{periods[i]}'] = df[f'{time}_Close'].rolling(window=l[i]).mean()
    return df[['Datetime',f'{time}_SMA_20',f'{time}_SMA_50',f'{time}_SMA_100',f'{time}_SMA_200']]
    
def check_sma(df,time):
    df.rename(columns={f'{time}_SMA_20':'SMA_20', f'{time}_SMA_50':'SMA_50', f'{time}_SMA_100':'SMA_100', f'{time}_SMA_200':'SMA_200'})
    pre_20=df['SMA_20'].iloc[-2]
    cur_20=df['SMA_20'].iloc[-1]
    pre_50=df['SMA_50'].iloc[-2]
    cur_50=df['SMA_50'].iloc[-1]
    pre_100=df['SMA_100'].iloc[-2]
    cur_100=df['SMA_100'].iloc[-1]
    pre_200=df['SMA_200'].iloc[-2]
    cur_200=df['SMA_200'].iloc[-1]
    df.drop(columns=['SMA_20', 'SMA_50', 'SMA_100', 'SMA_200'], inplace=True)
    message=""
    if(pre_20<pre_50 and cur_20>cur_50):
        message+="\n\t20 day SMA crosses above 50 day SMA"
    if(pre_20<pre_100 and cur_20>cur_100):
        message+="\n\t20 day SMA crosses above 100 day SMA"
    if(pre_20<pre_200 and cur_20>cur_200):
        message+="\n\t20 day SMA crosses above 200 day SMA"
    if(pre_50<pre_100 and cur_50>cur_100):
        message+="\n\t50 day SMA crosses above 100 day SMA" 
    if(pre_50<pre_200 and cur_50>cur_200):
        message+="\n\t50 day SMA crosses above 200 day SMA"
    if(pre_100<pre_100 and cur_100>cur_200):
        message+="\n\t100 day SMA crosses above 200 day SMA"
    if(pre_20>pre_50 and cur_20<cur_50):
        message+="\n\t20 day SMA crosses below 50 day SMA"
    if(pre_20>pre_100 and cur_20<cur_100):
        message+="\n\t20 day SMA crosses below 100 day SMA"
    if(pre_20>pre_200 and cur_20<cur_200):
        message+="\n\t20 day SMA crosses below 200 day SMA"
    if(pre_50>pre_100 and cur_50<cur_100):
        message+="\n\t50 day SMA crosses below 100 day SMA" 
    if(pre_50>pre_200 and cur_50<cur_200):
        message+="\n\t50 day SMA crosses below 200 day SMA"
    if(pre_100>pre_100 and cur_100<cur_200):
        message+="\n\t100 day SMA crosses below 200 day SMA"
    if message=="":
        return("No Update!")
    else:
        return(message)
    
def alert_sma(data,para1=20,para2=50,para3=100,para4=200):
    message = "\nSMA update : "
    
    data_15 = data.tail(para4 + 2)
    data_15=cal_sma(data_15, '15m',para1,para2,para3,para4)
    message += "\n*15 minute : *"+check_sma(data_15, '15m')
    
    filt_60 = (data['Datetime'].dt.minute == 15)
    data=data.loc[filt_60]
    data_60 = data.tail(para4 + 2)
    data_60=cal_sma(data_60, '60m',para1,para2,para3,para4)
    message += "\n*60 minute : *"+check_sma(data_60, '60m')
    
    filt_daily = (data['Datetime'].dt.hour == 9)
    data_daily = data.loc[filt_daily].tail(para4 + 2)
    data_daily=cal_sma(data_daily, '1d',para1,para2,para3,para4)
    message += f"\n*Daily : *"+check_sma(data_daily, '1d')
    
    if message == "\SMA update : ":
        message = "\nNo SMA update!"
    
    # send_whatsapp_messages("leads.csv", message)
    # send_email(message_text=message)
    return(message)

# while True:
    # print(stock)
    # sql_df = return_df(stock)
    # alert_rsi(data=sql_df)
    # alert_macd(data=sql_df)
    # alert_adx(data=sql_df)
    # alert_sma(data=sql_df)
    # alert_bb(data=sql_df)
    # time.sleep(5)

