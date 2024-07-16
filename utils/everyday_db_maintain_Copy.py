from warnings import filterwarnings

filterwarnings("ignore")
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table
import time
from essential_db_functions_Copy import *

import logging
import os

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

overall_start_time = time.time()

# Specify the directory path where you want to save the file
output_directory = "Log_files/"

# Ensure the directory exists, create it if necessary
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

current_datetime = datetime.now()
current_datetime_str = current_datetime.strftime("%Y_%m_%d_%I_%M_%S")

# Construct the full file path
log_file_path = os.path.join(
    output_directory, f"everyday_fetch_db_{current_datetime_str}.log"
)

# Create the log file
open(log_file_path, "w").close()

# Logging configuration
logging.basicConfig(
    filename=log_file_path, level=logging.INFO, format="%(asctime)s - %(message)s"
)

logging.info(f"\n\nDATABASE : {database_name}\n")

for table_name in table_names_list:

    start_time = time.time()

    try:

        df = pd.read_sql_table(table_name, con=engine)

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

        # print(f"\n Data for {table_name} fetched proper data \n {proper_df} \n\n")

        null_values_df = df[df["Datetime"] >= date_value]

        datetime_value = df.loc[proper_df.index[-1], "Datetime"]

        after_df = rerun_fetch_data(table_name, datetime_value)
        after_df["Datetime"] = after_df.index

        # print(f"\n Data for {table_name} fetched new data but before reseting index \n {after_df} \n\n")

        after_df.reset_index(drop=True, inplace=True)

        # print(f"\n Data for {table_name} fetched new data after reseting index \n {after_df} \n\n")

        final_df = pd.concat([proper_df, after_df])

        # final_df.to_csv(f"{table_name}_demo.csv")
        # ################################################################################################################

        # final_df[['1d_Open', '1d_High', '1d_Low', '1d_Close', '1d_Adj Close', '1d_Volume']] = final_df[['1d_Open', '1d_High', '1d_Low', '1d_Close', '1d_Adj Close', '1d_Volume']].ffill()

        # ################################################################################################################

        # fill the last two values of 1d_Open, 1d_High, 1d_Low, 1d_Close, 1d_Adj Close, 1d_Volume as null values
        # final_df.loc[final_df.index[-2]:, ['1d_Open', '1d_High', '1d_Low', '1d_Close', '1d_Adj Close', '1d_Volume']] = "1"
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

        # final_df.reset_index(drop=True, inplace=True)
        # final_df.to_csv(f"{table_name}_demo.csv")

        print(
            f"\n Data for {table_name} all concatenated successfully \n {final_df} \n\n"
        )

        # Delete the existing table
        table_to_delete = Table(table_name, metadata)
        table_to_delete.drop(engine)

        # Write the updated dataframe to PostgreSQL
        final_df.to_sql(table_name, engine, if_exists="replace", index=False)

        end_time = time.time()
        time_taken = end_time - start_time

        logging.info(f"Time taken for {table_name}: {time_taken} seconds")
        logging.info(f"Data processing for {table_name} completed successfully")

        # print(f"Time taken for {table_name}: {time_taken} seconds")
        # print(f"Fetching data for {table_name} is completed")

    except Exception as e:
        logging.error(f"Error occurred while processing table: {table_name}")
        logging.error(f"Error message: {e}")
        print(f"Error occurred while processing table: {table_name}")
        print(f"Error message: {e}")

        continue

    print(f"SUCCESSFULL UPDATION OF THE DB TABLE {table_name} IS DONE!")

overall_end_time = time.time()

logging.info(f"Overall time taken: {overall_end_time - overall_start_time} seconds")
logging.info("Data processing for all tables completed successfully")

print(f"Overall time taken: {overall_end_time - overall_start_time} seconds")
