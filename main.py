import concurrent
import threading

import numpy as np
import pandas as pd
import os
import datetime
import time
import requests
from binance import HistoricalKlinesType
from binance.client import Client

import constants
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

# Global counter and lock for thread-safe updates
fetch_counter = 0
counter_lock = threading.Lock()


def get_rate_limits():
    """
    Fetch the current used weight from Binance API.

    Returns:
        int: The current used weight.
    """

    url = f"https://fapi.binance.com/fapi/v1/exchangeInfo"
    response = requests.get(url)
    response.raise_for_status()
    request_weight_dict = \
        [rate_limit_dict for rate_limit_dict in response.json()['rateLimits'] if rate_limit_dict['rateLimitType'] == 'REQUEST_WEIGHT'][0]

    interval_in_seconds = int(request_weight_dict['intervalNum']) * (60 if request_weight_dict['interval'] == 'MINUTE' else 3600)

    return request_weight_dict['limit'], interval_in_seconds


request_weight_limit, request_weight_limit_interval = get_rate_limits()

used_request_weight = 0

# Initialize the Binance client
client = Client('', '')


def get_pairs_data_parallel(symbols: list, start_time: pd.Timestamp, end_time: pd.Timestamp) -> dict:
    """
    Fetch the last N historical kline data for given symbols and return it as a dictionary of DataFrames.

    Args:
        symbols (list): List of trading pair symbols.
        start_time (pd.Timestamp): The start_time of data fetching.

    Returns:
        dict: Dictionary containing the historical kline data for each symbol.
    """

    def fetch_data_for_symbol(symbol) -> pd.DataFrame | None:
        global fetch_counter
        global used_request_weight

        # Convert start_time to milliseconds
        start_time_ms = int(start_time.timestamp() * 1000)
        end_time_ms = int(end_time.timestamp() * 1000)

        with counter_lock:
            fetch_counter += 1
            print(f"Fetching {fetch_counter}/{len(symbols)} {symbol}")

        url = f"https://fapi.binance.com/fapi/v1/klines"

        try:

            # Fetch historical kline data using python-binance
            klines = client.get_historical_klines(
                symbol=symbol,
                interval=constants.timeframe,
                start_str=start_time_ms,
                end_str=end_time_ms,
                klines_type=HistoricalKlinesType.FUTURES
            )

        except Exception as e:
            print(e)
            return symbol, None

        # Convert UNIX timestamp to UTC time format and create DataFrame
        data = [[datetime.datetime.fromtimestamp(row[0] / 1000, datetime.UTC)] + row[1:5] for row in klines]

        pair_df = pd.DataFrame(data, columns=["time", "open", "high", "low", "close"])

        # Add the candle color to the return value
        pair_df_closes = pair_df.close.to_numpy()
        pair_df_opens = pair_df.open.to_numpy()
        pair_df['candle_color'] = np.where(pair_df_closes > pair_df_opens, 'green', 'red')

        # Convert columns to numeric types
        pair_df[["open", "high", "low", "close"]] = pair_df[["open", "high", "low", "close"]].apply(pd.to_numeric)

        return symbol, pair_df

    all_pairs_data = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=constants.max_threads) as executor:
        futures = {executor.submit(fetch_data_for_symbol, symbol): symbol for symbol in symbols}
        for future in concurrent.futures.as_completed(futures):
            symbol, pair_df = future.result()
            all_pairs_data[symbol] = pair_df

    return all_pairs_data


print('Timeframe: ', constants.timeframe)
print('Data starting time: ', constants.start_date)
print('Data ending time: ', constants.end_date)

my_pairs = pd.read_excel(constants.pairs_file_name, header=None)[0].tolist()

# Ensure the output directory exists
output_dir = f"./cached-data/{constants.timeframe}-{constants.end_date}"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

all_pairs_data = get_pairs_data_parallel(my_pairs, pd.to_datetime(constants.start_date), pd.to_datetime(constants.end_date))

# Write each DataFrame to an HDF5 file
for symbol, pair_df in all_pairs_data.items():
    if pair_df is not None:
        file_path = os.path.join(output_dir, f"{symbol}.hdf5")
        pair_df.to_hdf(file_path, key="pair_df", mode="w")


# Zip the directory after fetching all data
def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), os.path.basename(file))


zipf = zipfile.ZipFile(f"./cached-data/{constants.timeframe}-{constants.end_date}.zip", 'w', zipfile.ZIP_DEFLATED)
zipdir(f'./cached-data/{constants.timeframe}-{constants.end_date}/', zipf)
zipf.close()
