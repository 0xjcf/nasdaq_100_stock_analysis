import yfinance as yf
import ta

# Fetch historical data
ticker = "MDB"
data = yf.download(ticker, start="2023-01-01", end="2024-12-31")

# Calculate Bollinger Bands
data['BB_high'], data['BB_mid'], data['BB_low'] = ta.volatility.bollinger_hband(data['Close']), ta.volatility.bollinger_mavg(data['Close']), ta.volatility.bollinger_lband(data['Close'])

# Calculate RSI
data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()

# Example of identifying an oversold condition that might indicate a mean reversion opportunity
mean_reversion_opportunities = data[(data['Close'] < data['BB_low']) & (data['RSI'] < 30)]

print(mean_reversion_opportunities[['Close', 'BB_low', 'RSI']])
