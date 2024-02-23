from stock_analysis import get_stock_analysis, get_top_volatile_stocks
from options_data_utils import calculate_hv, display_debit_spread_data, fetch_vix

def main():
    while True:
        print("\nSelect an option:")
        print("1. Display data analysis for a specific stock")
        print("2. Identify top 10 most volatile NASDAQ-100 stocks with specified criteria")
        print("3. Fetch Options Chain Data and Highlight ATM/OTM Options")
        print("4. Calculate Historical Volatility for a specific stock")
        print("5. Display Historical VIX Value")

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
            print(f"\nCurrent VIX (Market Volatility Expectation): {vix:.2f}\n")
        else:
            print("\nInvalid choice. Please enter a valid option.\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting...")
