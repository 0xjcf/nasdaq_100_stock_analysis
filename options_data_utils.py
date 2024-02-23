import yfinance as yf
from diskcache import Cache
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

red_color_start = "\033[91m"
green_color_start = "\033[92m"
blue_color_start = "\033[94m"
gray_color_start = "\033[90m"
color_reset = "\033[0m"

cache = Cache('./cache')

def fetch_options_data_for_debit_spread(ticker, expiration_preference, expiration_length, bid_ask_spread_pct_threshold):
    # Convert expiration preference to actual date
    if expiration_preference == "days":
        target_date = datetime.now() + timedelta(days=expiration_length)
    elif expiration_preference == "weeks":
        target_date = datetime.now() + timedelta(weeks=expiration_length)
    elif expiration_preference == "months":
        target_date = datetime.now() + timedelta(days=30 * expiration_length)  # Approximation
    
    # Find the nearest expiration date to the target_date
    stock = yf.Ticker(ticker)
    options_dates = [datetime.strptime(date, '%Y-%m-%d') for date in stock.options]
    nearest_expiration_date = min(options_dates, key=lambda date: abs(date - target_date))
    cache_key = f"{ticker}_debit_spread_{nearest_expiration_date.strftime('%Y-%m-%d')}"

    if cache_key in cache:
        print(f"\n{blue_color_start}Loading debit spread data from cache for {ticker} for expiration {nearest_expiration_date.strftime('%Y-%m-%d')}.{color_reset}\n")
        debit_spreads = cache[cache_key]
    else:
        print(f"\n{green_color_start}Fetching debit spread data for {ticker}.{color_reset}\n")
        try:
            opts = stock.option_chain(nearest_expiration_date.strftime('%Y-%m-%d'))
            calls = opts.calls
            
            # Assume ATM is the strike closest to the current stock price
            stock_price = stock.history(period="1d")['Close'].iloc[-1]
            calls['type'] = np.where(calls['strike'] == stock_price, f"{blue_color_start}ATM{color_reset}",
                             np.where(calls['strike'] < stock_price, f"{green_color_start}ITM{color_reset}", f"{red_color_start}OTM{color_reset}"))
            
            # Filter and sort logic
            calls['bidAskSpreadPct'] = ((calls['ask'] - calls['bid']) / calls['ask']) * 100  # Calculate bid-ask spread percentage
            filtered_calls = calls[calls['bidAskSpreadPct'] <= bid_ask_spread_pct_threshold]  # Filter by bid-ask spread percentage threshold
            
            potential_spreads = []
            for i, call in filtered_calls.iterrows():
                # Assuming a basic structure for a debit spread: buying this call option
                # Risk-reward ratio: Simplified calculation (actual calculation may vary based on strategy)
                risk_reward_ratio = (call['strike'] + call['lastPrice']) / call['lastPrice']
                
                # Break-even analysis (for call options): strike price + premium paid
                break_even_price = call['strike'] + call['lastPrice']
                
                # Selecting based on highest open interest and implied volatility within filtered criteria
                spread = {
                    f"strike": call['strike'],
                    f"lastPrice": call['lastPrice'],
                    f"bid": call['bid'],
                    f"ask": call['ask'],
                    f"openInterest": call['openInterest'],
                    f"impliedVolatility": call['impliedVolatility'],
                    f"bidAskSpreadPct": call['bidAskSpreadPct'],
                    f"riskRewardRatio": risk_reward_ratio,
                    f"breakEvenPrice": break_even_price,
                    f"expirationDate": nearest_expiration_date.strftime('%Y-%m-%d'),
                    "": call['type']
                }
                potential_spreads.append(spread)
            
            # Sorting the potential spreads by open interest to select the top 10
            debit_spreads = pd.DataFrame(potential_spreads).sort_values(by='openInterest', ascending=False).head(10)
            cache.set(cache_key, debit_spreads, expire=86400)  # Cache for 24 hours
        except Exception as e:
            print(f"\n{red_color_start}An error occurred: {e}{color_reset}\n")
            debit_spreads = pd.DataFrame()
    
    return debit_spreads

def display_debit_spread_data(ticker):
    expiration_preference = input("Choose expiration preference (days, weeks, months): ")
    expiration_length = int(input("Enter the number for the expiration length: "))
    bid_ask_spread_threshold = float(input("Enter the acceptable bid-ask spread threshold: "))
    
    debit_spread_data = fetch_options_data_for_debit_spread(ticker, expiration_preference, expiration_length, bid_ask_spread_threshold)
    
    if not debit_spread_data.empty:
        print(f"\n{'='*40} Debit Call Spread Data for {ticker}: {'='*40}\n")
        print(debit_spread_data)
    else:
        print("No suitable debit call spreads found or no data to display.")
        
    return debit_spread_data

# Calculate Historical Volatility
def calculate_hv(ticker, period='1y'):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    # Calculate daily logarithmic returns
    log_returns = np.log(hist['Close'] / hist['Close'].shift(1))
    # Calculate standard deviation of log returns
    hv = log_returns.std() * np.sqrt(252)  # Annualize
    return hv

# Fetch VIX for market volatility expectations
def fetch_vix(period="1y"):
    vix = yf.Ticker("^VIX")
    current_vix = vix.history(period=period)['Close'].iloc[-1]
    return current_vix