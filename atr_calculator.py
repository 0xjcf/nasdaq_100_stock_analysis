import yfinance as yf
from diskcache import Cache
from market_time_utils import get_next_friday_market_close
import datetime

cache = Cache('./cache')

def calculate_14_day_ATR(ticker):
    cache_key = f"{ticker}_14_day_ATR"
    if cache_key in cache:
        print(f"Using cached ATR for {ticker}.")
        return cache[cache_key]
    
    print(f"Calculating ATR for {ticker}.")
    data = yf.download(ticker, period="3mo")
    if data.empty:
        print(f"Failed to fetch data for {ticker}.")
        return None

    data['High-Low'] = data['High'] - data['Low']
    data['High-PrevClose'] = abs(data['High'] - data['Close'].shift(1))
    data['Low-PrevClose'] = abs(data['Low'] - data['Close'].shift(1))
    data['TR'] = data[['High-Low', 'High-PrevClose', 'Low-PrevClose']].max(axis=1)
    data['ATR'] = data['TR'].rolling(window=14).mean()

    atr_value = data['ATR'].iloc[-1]
    expiration_time = get_next_friday_market_close()
    cache.set(cache_key, atr_value, expire=(expiration_time - datetime.datetime.now().timestamp()))

    return atr_value
