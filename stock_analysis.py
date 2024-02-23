import time
import ta
import yfinance as yf
import pandas as pd
from tqdm import tqdm
from diskcache import Cache
from atr_calculator import calculate_14_day_ATR
from market_time_utils import get_next_friday_market_close
from stock_data_utils import fetch_and_display_against_RSI, fetch_and_display_price_against_BB, fetch_weekly_range
from fundamental_analysis import fetch_fundamental_data, print_fundamental_data

# ANSI escape codes for colors
red_color_start = "\033[91m"
green_color_start = "\033[92m"
color_reset = "\033[0m"

cache = Cache('./cache')

def fetch_data_with_progress_bar(ticker):
    cache_key = f"{ticker}_data"
    if cache_key in cache:
        print(f"Loading data from cache for {ticker}.")
        return cache[cache_key]

    print(f"Fetching data for {ticker}.")
    for _ in tqdm(range(5), desc="Loading"):
        time.sleep(1)  # Simulate time delay for fetching
    
    try:
        data = yf.download(ticker, start='2024-01-01', end='2024-12-31', interval='1wk')
        if not data.empty:
            expiration_time = get_next_friday_market_close()
            cache.set(cache_key, data, expire=(expiration_time - time.time()))
            print("Data fetched successfully!")
            return data
    except Exception as e:
        print(f"Failed to fetch data: {e}")
        return None

def get_stock_analysis(ticker):
    print(f"\n{'='*40} Stock Analysis for {ticker} {'='*40}\n")
    # Fetch and display daily technical indicators
    fetch_weekly_range(ticker)
    # fetch_and_display_technical_indicators(ticker)
    fetch_and_display_price_against_BB(ticker)
    fetch_and_display_against_RSI(ticker)
    
    # Fetch and display fundamental data
    fundamental_data = fetch_fundamental_data(ticker)
    print_fundamental_data(fundamental_data)

def get_top_volatile_stocks(min_move, max_price):
    file_path = '/Users/jose/Dev/priceMovers/nasdaq-100-index-02-16-2024.csv'
    nasdaq_100_stocks = pd.read_csv(file_path)
    nasdaq_100_stocks['ATR'] = nasdaq_100_stocks['Symbol'].apply(calculate_14_day_ATR)

    nasdaq_100_stocks['Weekly Range'] = nasdaq_100_stocks['High'] - nasdaq_100_stocks['Low']
    volatile_stocks = nasdaq_100_stocks[(nasdaq_100_stocks['Weekly Range'] >= min_move) & (nasdaq_100_stocks['Last'] <= max_price)]
    top_volatile_stocks = volatile_stocks.sort_values(by='Weekly Range', ascending=False).head(10)

    print("\nTop 10 most volatile stocks with specified criteria in the NASDAQ-100:\n")
    for index, row in top_volatile_stocks.iterrows():
        print(f"{green_color_start}{row['Symbol']}: {row['Weekly Range']}{color_reset}")
    print("\n")

