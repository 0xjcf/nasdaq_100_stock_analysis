import diskcache as dc
from tqdm import tqdm
import yfinance as yf
import pandas as pd
import time
from atr_calculator import calculate_14_day_ATR

# ANSI escape codes for colors
red_color_start = "\033[91m"
green_color_start = "\033[92m"
color_reset = "\033[0m"

cache = dc.Cache('./cache')

def fetch_data_with_progress_bar(ticker):
    cache_key = f"{ticker}_data"
    # Check if data is in cache
    if cache_key in cache:
        print("Loading data from cache for", ticker)
        return cache[cache_key]
    
    print("Fetching data for", ticker)
    for _ in tqdm(range(5), desc="Loading"):
        time.sleep(1)  # Simulate time delay for fetching
    try:
        data = yf.download(ticker, start='2024-2-12', end='2024-2-16', interval='1wk')
        data['Weekly Range'] = data['High'] - data['Low']
        # Store fetched data in cache
        cache[cache_key] = data
        return data
    except Exception as e:
        print("Failed to fetch data:", e)
        return None

def get_weekly_range(ticker):
    data = fetch_data_with_progress_bar(ticker)
    if data is not None and not data.empty:
        print(f"\n{red_color_start}===========================================Weekly Range for {ticker}:==========================================={color_reset}", end="\n\n")
        print(data[['High', 'Low', 'Weekly Range']], end="\n\n")
    else:
        print("No data to display.")

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

def main():
    print("Select an option:")
    print("1. Display weekly range for a specific stock")
    print("2. Identify top 10 most volatile NASDAQ-100 stocks with specified criteria")

    choice = input("Enter your choice (1 or 2): ")

    if choice == '1':
        ticker = input("Enter the ticker symbol: ").upper()
        get_weekly_range(ticker)
    elif choice == '2':
        min_move = float(input("Enter the minimum dollar movement for the week: "))
        max_price = float(input("Enter the maximum price of the stock: "))
        get_top_volatile_stocks(min_move, max_price)
    else:
        print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()
