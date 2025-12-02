# test_binance.py
from src.api.connectors.binance_real import BinanceRealConnector
import os

# Initialize
api_key = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

connector = BinanceRealConnector(api_key, api_secret)

# Test connection
print("Testing Binance connection...")
if connector.validate_connection():
    print("✅ Connected to Binance")
    
    # Get balance
    balance = connector.get_balance()
    print(f"Balance: {balance}")
    
    # Get trades
    trades = connector.get_trades("ETHUSDT", limit=10)
    print(f"Trades: {trades}")
else:
    print("❌ Connection failed")
