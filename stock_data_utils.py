from diskcache import Cache
import yfinance as yf
import ta
import time
from market_time_utilities import get_next_friday_market_close

red_color_start = "\033[91m"
green_color_start = "\033[92m"
blue_color_start = "\033[94m"
color_reset = "\033[0m"

cache = Cache('./cache')

def fetch_weekly_range(ticker):
    cache_key = f"{ticker}_weekly_range"
    try:
        if cache_key in cache:
            print(f"\n{blue_color_start}Loading weekly range from cache for {ticker}.{color_reset}\n")
            weekly_data = cache[cache_key]
        else:
            print(f"\n{green_color_start}Fetching weekly range data for {ticker}.{color_reset}\n")
            weekly_data = yf.download(ticker, period='1wk', interval='1wk')
            if not weekly_data.empty:
                weekly_data['Weekly Range'] = weekly_data['High'] - weekly_data['Low']
                expiration_time = get_next_friday_market_close() - time.time()
                cache.set(cache_key, weekly_data, expire=expiration_time)
            else:
                print(f"\n{red_color_start}Failed to fetch weekly data.{color_reset}\n")
        
        if not weekly_data.empty:
            print(weekly_data[['High', 'Low', 'Weekly Range']])
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
