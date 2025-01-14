from dotenv import dotenv_values
import argparse
import datetime

params = dotenv_values("./.env.params")

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("--timeframe", help="Set the timeframe for candles")
parser.add_argument('--pl', help="Set the pair list filename")
parser.add_argument('--threads', help='Set the number of threads to use')
args = parser.parse_args()

timeframe = args.timeframe if args.timeframe is not None else "1h"
pairs_file_name = args.pl if args.pl is not None else params["pairs_file_name"]
max_threads = int(args.threads) if args.threads is not None else 1

end_date = datetime.datetime.strptime(params["end_date"], "%Y-%m-%d").strftime("%d %B %Y")
start_date = datetime.datetime.strptime(params["start_date"], "%Y-%m-%d").strftime("%d %B %Y")
