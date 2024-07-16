from sqlalchemy import create_engine
from warnings import filterwarnings

# Suppress warnings
filterwarnings("ignore")
import time
from essential_db_functions_Copy import *
import logging
import os
from datetime import datetime, timedelta

# Set PostgreSQL connection parameters
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

# List of stocks1
# stocks = ["^NSEI", "^NSEBANK", "ZYDUSLIFE", "HDFCBANK", "AXISBANK"]

stocks = ['acc', 'acl', 'adanient', 'adaniports', 'adanipower', 'alkem', '^NSEI', 'axisbank', 'bajaj-auto', 'bajajfinsv', 'bajfinance', 'biocon', 'boschltd', 'bpcl', 'britannia', 'canbk', 'cgpower', 'cholafin', 'cipla', 'coalindia', 'coforge', 'colpal', 'ltim', 'ltts', 'lupin', 'm&m', 'prestige', 'sbicard', 'sbilife', 'sbin', 'shreecem', 'muthootfin', 'titan', 'torntpharm', 'abb', 'industower', 'voltas', 'bhartiartl', 'bhel', 'pnb', 'policybzr', 'abfrl', 'polycab', 'shriramfin', 'siemens', 'sonacoms', 'srf', 'sunpharma', 'suntv', 'syngene', 'tatachem', 'tatacomm', 'tataconsum', 'tataelxsi', 'tatamotors', 'tatamtrdvr', 'itc', 'jindalstel', 'ramcocem', 'recltd', 'infy', 'ioc', 'tatapower', 'tatasteel', 'ipcalab', 'irctc', '^NSEBANK', 'YESBANK', 'ZYDUSLIFE', 'balkrisind', 'bankbaroda', 'bataindia', 'bdl', 'bel', 'bergepaint', 'bharatforg', 'concor', 'coromandel', 'crompton', 'cumminsind', 'reliance', 'sail', 'dalbharat', 'deepakntr', 'msumi', 'powergrid', 'epigral', 'escorts', 'fact', 'fluorochem', 'gail', 'gland', 'delhivery', 'divislab', 'dixon', 'dlf', 'drreddy', 'eichermot', 'm&mfin', 'mankind', 'marico', 'maruti', 'maxhealth', 'mazdock', 'mcdowell-n', 'mfsl', 'motherson', 'jswenergy', 'jswsteel', 'jublfood', 'kotakbank', 'ambujacem', 'aplapollo', 'naukri', 'mphasis', 'godrejprop', 'dabur', 'grasim', 'gujgasltd', 'hal', 'havells', 'kpittech', 'l&tfh', 'latentview', 'lauruslabs', 'lichsgfin', 'lici', 'hcltech', 'hdfcamc', 'hdfcbank', 'hdfclife', 'irfc', 'ubl', 'ultracemco', 'unionbank', 'upl', 'vbl', 'vedl', 'godrejcp', 'wipro', 'pel', 'trent', 'tvsmotor', 'aartiind', 'persistent', 'petronet', 'pfc', 'pghh', 'pidilitind', 'piind', 'tcs', 'techm', 'tiindia', 'navinfluor', 'nestleind', 'nhpc', 'nmdc', 'ntpc', 'nykaa', 'oberoirlty', 'oil', 'ongc', 'pageind', 'patanjali', 'heromotoco', 'hindalco', 'hindpetro', 'hindunilvr', 'icicibank', 'icicigi', 'icicipruli', 'idfcfirstb', 'igl', 'indhotel', 'indigo', 'indusindbk', 'apollohosp', 'apollotyre', 'asianpaint', 'lodha', 'lt', 'astral', 'aubank', 'auropharma', 'abcapital']
# print(len(stocks))

overall_start_time = time.time()

# Create a directory for log files if it doesn't exist
log_directory = "Log_files/"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

current_datetime = datetime.now()
current_datetime_str = current_datetime.strftime("%Y_%m_%d_%I_%M_%S")

# Define the log file path
log_file_path = os.path.join(
    log_directory, f"initial_fetch_log_{current_datetime_str}.log"
)

# Configure logging
logging.basicConfig(
    filename=log_file_path, level=logging.INFO, format="%(asctime)s - %(message)s"
)
logging.info(f"\n\nDATABASE : {database_name}\n")

before_2m_date = (datetime.now() - timedelta(days=55)).strftime("%Y-%m-%d")
print(
    f"*********************************\n{before_2m_date}\n*********************************"
)

# Loop through each stock
for symbol in stocks:
    start_time = time.time()
    date = before_2m_date

    try:
        data = initial_fetch_data(symbol, date, conn)
        logging.info(
            f"Fetching data for {symbol} is completed from {date} till {data.tail(1)['Date'].values[0]}"
        )
        print(f"Fetching data for {symbol} is completed")

    except Exception as e:
        logging.error(f"Error occurred while fetching data for {symbol}: {str(e)}")
        print(f"Error occurred while fetching data for {symbol}: {str(e)}")

        continue

    end_time = time.time()
    time_taken = end_time - start_time

    logging.info(f"Time taken for {symbol}: {time_taken} seconds")
    print(f"Time taken for {symbol}: {time_taken} seconds")

overall_end_time = time.time()

logging.info(f"Overall time taken: {overall_end_time - overall_start_time} seconds")

print(f"Overall time taken: {overall_end_time - overall_start_time} seconds")

# Example of reading data from PostgreSQL for a specific stock
table_name = "HDFCBANK"
data_new = pd.read_sql_table(table_name, engine)
print(data_new)
# data_new.to_csv(f"{table_name}_demo.csv", index=False)
