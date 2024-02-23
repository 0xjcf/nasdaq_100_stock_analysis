import time
import yfinance as yf
from diskcache import Cache
from market_time_utils import get_next_friday_market_close

# ANSI escape code for blue color
red_color_start = "\033[91m"
green_color_start = "\033[92m"
blue_color_start = "\033[94m"
color_reset = "\033[0m"

# Initialize cache outside of the function if it's not already initialized
cache = Cache('./cache')

def fetch_fundamental_data(ticker):
    cache_key = f"{ticker}_fundamental_data"
    if cache_key in cache:
        print(f"\n{blue_color_start}Loading fundamental data from cache for {ticker}.{color_reset}\n")
        return cache[cache_key]

    print(f"\n{green_color_start}Fetching fundamental data for {ticker}.\n{color_reset}")
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        fundamental_data = {
            "PE Ratio": info.get('forwardPE', 'N/A'),
            "EPS": info.get('trailingEps', 'N/A'),
            "Profit Margins": info.get('profitMargins', 'N/A'),
            "Return on Assets": info.get('returnOnAssets', 'N/A'),
            "Free Cash Flow": info.get('freeCashflow', 'N/A'),
            "Operating Cash Flow": info.get('operatingCashflow', 'N/A'),
            "Debt to Equity": info.get('debtToEquity', 'N/A'),
            "Revenue Growth": info.get('revenueGrowth', 'N/A'),
            "Gross Margins": info.get('grossMargins', 'N/A'),
            "Analyst Target Mean Price": info.get('targetMeanPrice', 'N/A'),
            "Analyst Recommendation": info.get('recommendationKey', 'N/A'),
        }
        
        # Cache the fetched fundamental data with expiration
        expiration_time = get_next_friday_market_close() - time.time()
        cache.set(cache_key, fundamental_data, expire=expiration_time)

        return fundamental_data
    except Exception as e:
        print(f"\n{red_color_start}Failed to fetch fundamental data for {ticker}: {e}{color_reset}\n")
        return {}

def print_fundamental_data(fundamental_data):
    for key, value in fundamental_data.items():
        print(f"{key}: {value}")
    print("\n")
