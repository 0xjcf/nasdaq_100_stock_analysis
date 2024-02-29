import os
import pickle
from diskcache import Cache
from tqdm import tqdm

import yfinance as yf
import pandas as pd
import ta
import time
from market_time_utils import get_next_friday_market_close

red_color_start = "\033[91m"
green_color_start = "\033[92m"
blue_color_start = "\033[94m"
color_reset = "\033[0m"

cache = Cache('./cache')

current_directory = os.path.dirname(__file__)

csv_file_path = os.path.join(current_directory, 'stocks-screener-02-29-2024.csv')

def fetch_data_with_progress_bar(ticker):
    """Fetch historical data with a loading indicator."""
    print(f"Fetching data for {ticker}...")
    for _ in tqdm(range(1), desc=f"Loading {ticker}"):
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y")
            if hist.empty:
                return None, "No data"
            return hist, None
        except Exception as e:
            return None, str(e)

def fetch_weekly_range(ticker):
    cache_key = f"{ticker}_weekly_range"
    try:
        if cache_key in cache:
            print(f"\n{blue_color_start}Loading weekly range from cache for {ticker}.{color_reset}\n")
            weekly_data = cache[cache_key]
        else:
            print(f"\n{green_color_start}Fetching weekly range data for {ticker}.{color_reset}\n")
            weekly_data = yf.download(ticker, period='12wk', interval='1wk')
            if not weekly_data.empty:
                weekly_data['Weekly Range'] = weekly_data['High'] - weekly_data['Low']
                expiration_time = get_next_friday_market_close() - time.time()
                cache.set(cache_key, weekly_data, expire=expiration_time)
            else:
                print(f"\n{red_color_start}Failed to fetch weekly data.{color_reset}\n")
        
        if not weekly_data.empty:
            print(weekly_data[['High', 'Low', 'Close', 'Weekly Range']])
    except Exception as e:
        print(f"\n{red_color_start}An error occurred while fetching weekly range for {ticker}: {e}{color_reset}\n")

def fetch_and_display_technical_indicators(ticker):
    cache_key = f"{ticker}_daily_technical_indicators"
    try:
        if cache_key in cache:
            print(f"\n{blue_color_start}Loading daily technical indicators from cache for {ticker}.{color_reset}\n")
            daily_data = cache[cache_key]
        else:
            print(f"\n{green_color_start}Fetching daily data for technical indicators for {ticker}.{color_reset}\n")
            daily_data = yf.download(ticker, period='3mo', interval='1d')
            if not daily_data.empty:
                daily_data['RSI'] = ta.momentum.RSIIndicator(daily_data['Close']).rsi()
                daily_data['BB_high'] = ta.volatility.bollinger_hband(daily_data['Close'])
                daily_data['BB_mid'] = ta.volatility.bollinger_mavg(daily_data['Close'])
                daily_data['BB_low'] = ta.volatility.bollinger_lband(daily_data['Close'])
                expiration_time = get_next_friday_market_close() - time.time()
                cache.set(cache_key, daily_data, expire=expiration_time)
            else:
                print(f"\n{red_color_start}Failed to fetch daily data.{color_reset}\n")
        
        if not daily_data.empty:
            print("\nDaily Technical Indicators (RSI and Bollinger Bands):\n")
            print(daily_data[['RSI', 'BB_high', 'BB_mid', 'BB_low']].tail())
    except Exception as e:
        print(f"\n{red_color_start}An error occurred while fetching daily technical indicators for {ticker}: {e}{color_reset}\n")


def calculate_bollinger_bands(prices, window=20, no_of_stds=2):
    """
    Calculate Bollinger Bands for a given set of prices.
    
    :param prices: Pandas Series of stock prices.
    :param window: The period for calculating the moving average.
    :param no_of_stds: The number of standard deviations to consider for the band width.
    :return: A DataFrame with columns for the Bollinger Bands (upper_band, lower_band) and moving average (ma).
    """
    rolling_mean = prices.rolling(window=window).mean()
    rolling_std = prices.rolling(window=window).std()
    
    upper_band = rolling_mean + (rolling_std * no_of_stds)
    lower_band = rolling_mean - (rolling_std * no_of_stds)
    
    return pd.DataFrame({'ma': rolling_mean, 'upper_band': upper_band, 'lower_band': lower_band})


def fetch_and_display_price_against_BB(ticker):
    # Fetch historical data
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")  # Example period
    close_prices = hist['Close']
    
    # Calculate Bollinger Bands
    bollinger_bands = calculate_bollinger_bands(close_prices)
    
    # Fetch the latest price
    latest_price = close_prices.iloc[-1]
    
    # Compare the latest price to the Bollinger Bands
    latest_band_data = bollinger_bands.iloc[-1]
    print(f"\nLatest price for {ticker}: {latest_price}\n")
    print(f"Bollinger Bands (Latest):")
    print(f" - Upper Band: {latest_band_data['upper_band']}")
    print(f" - Moving Average: {latest_band_data['ma']}")
    print(f" - Lower Band: {latest_band_data['lower_band']}")
    
    # Indicate the position of the latest price relative to the Bollinger Bands
    if latest_price > latest_band_data['upper_band']:
        print("\nThe latest price is above the upper Bollinger Band.\n")
    elif latest_price < latest_band_data['lower_band']:
        print("\nThe latest price is below the lower Bollinger Band.\n")
    else:
        print("\nThe latest price is within the Bollinger Bands.\n")
        
def calculate_rsi(prices, window=14):
    """
    Calculate the Relative Strength Index (RSI) for a given set of prices.
    
    :param prices: Pandas Series of stock prices.
    :param window: The period (number of days) over which to calculate the RSI.
    :return: A Pandas Series containing the RSI values.
    """
    delta = prices.diff(1)
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=window, min_periods=1).mean()
    avg_loss = loss.rolling(window=window, min_periods=1).mean()

    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))
    
    return rsi        
        
def fetch_and_display_against_RSI(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")  # Fetch 6 months of historical data
    close_prices = hist['Close']
    
    # Calculate RSI using the refined function
    rsi = calculate_rsi(close_prices)
    latest_rsi = rsi.iloc[-1]

    print(f"RSI (Latest): {latest_rsi:.2f}")
    
    # Analyze the latest RSI value for overbought/oversold conditions
    if latest_rsi > 70:
        print("\nThe RSI indicates the stock is in overbought territory.\n")
    elif latest_rsi < 30:
        print("\nThe RSI indicates the stock is in oversold territory.\n")
    else:
        print("\nThe RSI is within normal range.\n")
        
def filter_extreme_stocks():
    file_path = csv_file_path
    stock_list = pd.read_csv(file_path)['Symbol'].tolist()
    extreme_stocks = []
    
    for ticker in tqdm(stock_list, desc="Analyzing stocks", colour='green'):
        # Check cache first
        cached_data = cache.get(ticker)
        if cached_data:
            hist, error = pickle.loads(cached_data), None
        else:
            hist, error = fetch_data_with_progress_bar(ticker)
            if hist is not None:
                cache.set(ticker, pickle.dumps(hist), expire=86400)  # Cache for 1 day

        if error or hist is None:
            print(f"Error fetching data for {ticker}: {error}")
            continue

        close_prices = hist['Close']
        bollinger_bands = calculate_bollinger_bands(close_prices)
        rsi = calculate_rsi(close_prices)
        
        latest_price = close_prices.iloc[-1]
        latest_upper_band = bollinger_bands['upper_band'].iloc[-1]
        latest_lower_band = bollinger_bands['lower_band'].iloc[-1]
        latest_rsi = rsi.iloc[-1]

        # Check for extreme conditions
        if (latest_price >= latest_upper_band and latest_rsi >= 70) or \
           (latest_price <= latest_lower_band and latest_rsi <= 30):
            extreme_stocks.append((ticker, latest_price, latest_rsi, latest_upper_band, latest_lower_band))
    
    # Sort and limit the list based on your criteria
    extreme_stocks.sort(key=lambda x: -x[2])  # Example: Sort by RSI value, descending
    return extreme_stocks[:10]