from clear_cache import clear_data_cache
from stock_analysis import get_stock_analysis, get_top_volatile_stocks
from options_data_utils import calculate_hv, display_debit_spread_data, fetch_vix
from stock_data_utils import filter_extreme_stocks

green_color_start = "\033[92m"
orange_color_start = "\033[38;5;208m"
color_reset = "\033[0m"

def main():
    while True:
        print("\nSelect an option:")
        print("1. Display data analysis for a specific stock")
        print("2. Identify top 10 most volatile NASDAQ-100 stocks with specified criteria")
        print("3. Fetch Options Chain Data and Highlight ATM/OTM Options")
        print("4. Calculate Historical Volatility for a specific stock")
        print("5. Display Historical VIX Value")
        print("6. Filter extreme level stocks")
        print("7. Clear the cache (Set to clear every Friday after market hours)")

        choice = input("\nEnter your choice or type 'exit' to quit: ").strip().lower()  # .strip() removes any leading/trailing whitespace
            
        if choice == 'exit':  # Check if the user wants to exit
            print("Exiting program. Goodbye!")
            break  # Exit the loop and end the program
        elif choice == '1':
            ticker = input("Enter the ticker symbol: ").upper()
            get_stock_analysis(ticker)
        elif choice == '2':
            min_move = float(input("Enter the minimum dollar movement for the week: "))
            max_price = float(input("Enter the maximum price of the stock: "))
            get_top_volatile_stocks(min_move, max_price)
        elif choice == '3':
            ticker = input("Enter the ticker symbol: ").upper()
            display_debit_spread_data(ticker)
        elif choice == '4':
            ticker = input("Enter the ticker symbol: ").upper()
            hv = calculate_hv(ticker)
            print(f"\nHistorical Volatility (Annualized) for {ticker}: {hv:.2%}\n")
        elif choice == '5':
            vix = fetch_vix()
            print(f"\nHistorical VIX (Market Volatility Expectation - Annualized): {vix:.2f}\n")
        elif choice == '6':
            extreme_stocks = filter_extreme_stocks()
            print("\nTop Extreme Level Stocks:")
            for stock in extreme_stocks:
                print(f"{orange_color_start}Ticker: {stock[0]}, Latest Price: {stock[1]}, RSI: {stock[2]}, Upper Band: {stock[3]}, Lower Band: {stock[4]}{color_reset}")
        elif choice == '7':
            print("Clearing the cache...")
            clear_data_cache()
            # Clear the cache here
            print("Cache cleared successfully.")
        else:
            print("\nInvalid choice. Please enter a valid option.\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting...")
