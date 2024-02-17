import yfinance as yf
import time
import diskcache as dc
from datetime import datetime

cache = dc.Cache('./cache')

def calculate_14_day_ATR(ticker, cache_duration=7):
    cache_key = f"{ticker}_ATR"
    if cache_key in cache:
        cached_atr, cache_date = cache[cache_key]
        if (datetime.now() - cache_date).days < cache_duration:
            print(f"Using cached ATR for {ticker}.")
            return cached_atr

    print(f"Fetching data for {ticker}.")
    time.sleep(1)  # Rate limiting

    data = yf.download(ticker, period="1y")
    if data.empty:
        print(f"Failed to fetch data for {ticker}.")
        return None

    data['High-Low'] = data['High'] - data['Low']
    data['High-PrevClose'] = abs(data['High'] - data['Adj Close'].shift(1))
    data['Low-PrevClose'] = abs(data['Low'] - data['Adj Close'].shift(1))
    data['TR'] = data[['High-Low', 'High-PrevClose', 'Low-PrevClose']].max(axis=1)
    data['ATR'] = data['TR'].rolling(window=14).mean()

    atr_value = data['ATR'].iloc[-1]
    cache[cache_key] = (atr_value, datetime.now())
    return atr_value
