import pandas as pd
import numpy as np
import yfinance as yf
from sqlalchemy import create_engine
from datetime import datetime
from warnings import filterwarnings

filterwarnings("ignore")


def select_database(database_name):

    db = database_name

    return db


def create_db_engine(user, password, host_name, database_name):
    """
    Creates a connection to the MySQL database.
    """
    init_engine = create_engine(
        f"mysql+mysqlconnector://{user}:{password}@{host_name}/{database_name}"
    )
    return init_engine


def connect_to_engine(engine):
    conn = engine.connect()
    return conn


#############################################################################################################################################################################
# Initial Fetch Data
#############################################################################################################################################################################


def initial_fetch_data(symbol, date, conn):

    if symbol == "^NSEI" or symbol == "^NSEBANK":
        symbol = symbol.upper()
    else:
        symbol = f"{symbol}.NS".upper()

    date = datetime.strptime(date, "%Y-%m-%d")
    temp_end = datetime.strptime("2024-06-01", "%Y-%m-%d")

    # Download 15-minute data
    min15 = yf.download(symbol, start=date, end=temp_end, interval="15m")
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
    min60 = yf.download(symbol, start=date, end=temp_end, interval="60m")
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
    day1 = yf.download(symbol, start=date, end=temp_end, interval="1d")
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

    if symbol == "^NSEI" or symbol == "^NSEBANK":
        main_df.to_sql(
            symbol, conn, if_exists="append", index=True, index_label="Datetime"
        )
    else:
        main_df.to_sql(
            symbol[:-3], conn, if_exists="append", index=True, index_label="Datetime"
        )

    return main_df


#############################################################################################################################################################################
# Everyday Fetch Data
#############################################################################################################################################################################


def fetch_table_names(engine, metadata):
    """
    Fetches the table names from the database.
    """
    metadata.reflect(engine)

    table_names = metadata.tables.keys()

    table_list = []
    for table_name in table_names:
        table_list.append(table_name)

    return table_list


def rerun_fetch_data(symbol, date):

    if symbol == "^NSEI" or symbol == "^NSEBANK":
        symbol = symbol.upper()
    else:
        symbol = f"{symbol}.NS".upper()

    date = datetime.strptime(str(date), "%Y-%m-%d %H:%M:%S")

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
    # min15 = min15.resample("5T").ffill()

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

    # print(f"\n Raw data for {symbol} is {day1}\n\n")
    day1.index = day1.index.strftime("%Y-%m-%d %H:%M:%S")
    day1.index = pd.to_datetime(day1.index)
    day1["Date"] = day1.index.date
    for i in range(len(day1.columns)):
        day1.columns.values[i] = "1d_" + day1.columns.values[i]

    # print(f"\n Raw data after created date column for {symbol} is {day1}\n\n")

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

    # Extend the index to the end of the day
    last_timestamp = day1.index[-1]
    end_of_day = last_timestamp.replace(hour=23, minute=59, second=59)
    new_index = pd.date_range(start=day1.index[0], end=end_of_day, freq="T")
    day1 = day1.reindex(new_index)

    # print(f"\n final data after reindexing columns before splitting it into 5 mins for {symbol} is {day1}\n\n")
    day1 = day1.resample("15min").ffill()
    day1.fillna(method="ffill", inplace=True)

    print(f"\n final data after resampling for {symbol} is {day1}\n\n")

    # Concatenate dataframes
    main_df = pd.concat([min15, min60, day1], axis=1)
    # Drop duplicate columns
    main_df = main_df.loc[:, ~main_df.columns.duplicated()]
    # pd.set_option('display.max_rows', None)
    main_df = main_df.dropna(subset=["15m_Open", "15m_High", "15m_Low", "15m_Close"])

    print(f"\n Full & final data for {symbol} is {main_df}\n\n")

    return main_df


#############################################################################################################################################################################
