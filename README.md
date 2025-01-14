# Binance Historical Data Fetcher

This project fetches historical kline data for specified trading pairs from the Binance API and saves the data to HDF5 files. The data is then
compressed into a ZIP file for easy storage and transfer.

## Prerequisites

- Python 3.8 or higher
- `pip` package manager

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/thewitcher745/candlestick-data-caching
    cd candlestick-data-caching
    ```

2. Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

1. Customize the `.env.params` file in the root directory with your desired inputs

2. Update the `start_date`, `end_date`, and `pairs_file_name` as needed.

## Usage

1. Prepare an Excel file containing the list of trading pairs. The file name should match the `pairs_file_name` specified in the `.env.params` file.

2. Run the script:

    ```bash
    python main.py --timeframe <timeframe> --pl <pairs_file_name> --threads <number_of_threads>
    ```

    - `--timeframe`: Set the timeframe for candles (default: "1h").
    - `--pl`: Set the pair list filename (default: value from `.env.params`).
    - `--threads`: Set the number of threads to use (default: 1).

## Output

The script will create a directory named `cached-data/<timeframe>-<end_date>` and save each trading pair's data as an HDF5 file in this directory.
After fetching all data, the directory will be compressed into a ZIP file.

## Example

```bash
python main.py --timeframe 1h --pl "futures_pairs - 202411.xlsx" --threads 10