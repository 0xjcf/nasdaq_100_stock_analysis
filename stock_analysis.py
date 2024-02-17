import yfinance as yf
from dotenv import load_dotenv
import pandas as pd
from atr_calculator import calculate_14_day_ATR

# Load environment variables from .env file
load_dotenv()

# ANSI escape codes for red color to highlight output
red_color_start = "\033[91m"
color_reset = "\033[0m"


def get_weekly_range(ticker):
    data = yf.download(ticker, start='2024-2-12', end='2024-2-16', interval='1wk')
    data['Weekly Range'] = data['High'] - data['Low']
    stocks_with_large_moves = data[data['Weekly Range'] > 10]
    print(f"\n{red_color_start}===========================================Weekly Range for {ticker}:==========================================={color_reset}", end="\n\n")
    print(stocks_with_large_moves, end="\n\n")

def get_top_volatile_stocks():
    """
    Identifies the top 10 most volatile NASDAQ-100 stocks with at least $10 weekly movement
    from the provided CSV file.
    """
    # Path to the CSV file containing NASDAQ-100 index constituents
    file_path = '/Users/jose/Dev/priceMovers/nasdaq-100-index-02-16-2024.csv'
    nasdaq_100_stocks = pd.read_csv(file_path)
    nasdaq_100_stocks['ATR'] = nasdaq_100_stocks['Symbol'].apply(calculate_14_day_ATR)

    
    # Calculate the weekly range for each stock as the difference between the high and low prices
    nasdaq_100_stocks['Weekly Range'] = nasdaq_100_stocks['High'] - nasdaq_100_stocks['Low']
    
    # Filter stocks that have at least $10 movement in their weekly range
    volatile_stocks = nasdaq_100_stocks[(nasdaq_100_stocks['Weekly Range'] >= 10) & (nasdaq_100_stocks['Last'] < 1000)]
    
    # Identify the top 10 most volatile stocks based on their weekly range
    top_volatile_stocks = volatile_stocks.sort_values(by='Weekly Range', ascending=False).head(10)
    
    # ANSI escape code for green color
    green_color_start = "\033[92m"
    
    print("\nTop 10 most volatile stocks with at least $10 weekly movement in the NASDAQ-100:")
    for index, row in top_volatile_stocks.iterrows():
        print(f"{green_color_start}{row['Symbol']}: {row['Weekly Range']}{color_reset}")

def main():
    """
    Main function to run the script. Provides a user menu to choose between functionalities.
    """
    print("Select an option:")
    print("1. Display weekly range for a specific stock")
    print("2. Identify top 10 most volatile NASDAQ-100 stocks with at least $10 weekly movement")

    choice = input("Enter your choice (1 or 2): ")

    if choice == '1':
        ticker = input("Enter the ticker symbol: ").upper()
        get_weekly_range(ticker)
    elif choice == '2':
        get_top_volatile_stocks()
    else:
        print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()


