from binance.client import Client
from app.config import settings
from typing import Optional, Dict, List

class ExchangeService:
    def __init__(self):
        if settings.BINANCE_API_KEY and settings.BINANCE_API_SECRET:
            self.binance_client = Client(
                api_key=settings.BINANCE_API_KEY,
                api_secret=settings.BINANCE_API_SECRET
            )
        else:
            self.binance_client = None
    
    def get_account_balance(self) -> Optional[Dict]:
        """Obtener balance de cuenta Binance"""
        if not self.binance_client:
            return None
        
        try:
            account = self.binance_client.get_account()
            balances = {b['asset']: float(b['free']) for b in account['balances']}
            return balances
        except Exception as e:
            print(f"Error fetching balance: {str(e)}")
            return None
    
    def get_exchange_info(self) -> Optional[Dict]:
        """Obtener información de exchange"""
        if not self.binance_client:
            return None
        
        try:
            return self.binance_client.get_exchange_info()
        except Exception as e:
            print(f"Error fetching exchange info: {str(e)}")
            return None
    
    def get_ticker(self, symbol: str) -> Optional[Dict]:
        """Obtener ticker de símbolo"""
        if not self.binance_client:
            return None
        
        try:
            return self.binance_client.get_symbol_info(symbol)
        except Exception as e:
            print(f"Error fetching ticker: {str(e)}")
            return None

exchange_service = ExchangeService()
