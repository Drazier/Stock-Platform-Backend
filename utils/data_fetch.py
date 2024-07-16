import json
import pandas as pd
import yfinance as yf
from datetime import datetime
from sqlalchemy import create_engine, MetaData
from warnings import filterwarnings

filterwarnings("ignore")


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

    day1 = day1.resample("15min").ffill()
    day1.fillna(method="ffill", inplace=True)

    # Concatenate dataframes
    main_df = pd.concat([min15, min60, day1], axis=1)
    main_df = main_df.loc[:, ~main_df.columns.duplicated()]
    main_df = main_df.dropna(subset=["15m_Open", "15m_High", "15m_Low", "15m_Close"])

    return main_df


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

user_name = "postgres"
user_password = "root"
host = "localhost"
port = "5432"
database_name = "Demo"

# PostgreSQL connection string
postgres_connection_string = (
    f"postgresql://{user_name}:{user_password}@{host}:{port}/{database_name}"
)

# Create the connection to the database
engine = create_engine(postgres_connection_string)

conn = connect_to_engine(engine)

# Reflect the database tables
metadata = MetaData()
metadata.reflect(bind=engine)

table_names_list = metadata.tables.keys()


def fetch_data(ticker_symbol):

    if ticker_symbol in table_names_list:

        df = pd.read_sql_table(ticker_symbol, con=engine)

        # Find the starting index of the latest chunk of consecutive null-filled values
        null_chunks = df["1d_Open"].isnull().astype(int).diff().fillna(0)
        latest_chunk_start_index = null_chunks[null_chunks == 1].index[-1]

        # Getting time for it
        # date_value = df.loc[latest_chunk_start_index, 'Datetime']
        date_value = df.loc[latest_chunk_start_index, "Datetime"].strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # split data according to the date in two parts
        proper_df = df[df["Datetime"] < date_value]

        datetime_value = df.loc[proper_df.index[-1], "Datetime"]

        after_df = rerun_fetch_data(ticker_symbol, datetime_value)
        after_df["Datetime"] = after_df.index

        after_df.reset_index(drop=True, inplace=True)

        final_df = pd.concat([proper_df, after_df])

        # # fill the last two values of 1d_Open, 1d_High, 1d_Low, 1d_Close, 1d_Adj Close, 1d_Volume as null values
        final_df.iloc[
            -2:,
            final_df.columns.get_indexer(
                [
                    "1d_Open",
                    "1d_High",
                    "1d_Low",
                    "1d_Close",
                    "1d_Adj Close",
                    "1d_Volume",
                ]
            ),
        ] = None

        final_df.reset_index(drop=True, inplace=True)

        # fill the null values with the previous values
        final_df.fillna(method="ffill", inplace=True)

        final_dict = final_df.to_dict(orient="records")

        # Serialize to JSON
        with open(f"{ticker_symbol}.json", "w") as f:
            json.dump(final_dict, f, default=str)

        return final_dict

    else:

        return f"Table {ticker_symbol} does not exist in the database."
