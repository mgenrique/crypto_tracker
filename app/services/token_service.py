import requests
from typing import Dict, List, Optional
import asyncio

class TokenService:
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    @staticmethod
    def get_price(symbol: str) -> Optional[Dict]:
        """Obtener precio de token desde CoinGecko"""
        try:
            url = f"{TokenService.BASE_URL}/simple/price"
            params = {
                "ids": symbol.lower(),
                "vs_currencies": "usd",
                "include_market_cap": "true",
                "include_24hr_vol": "true",
                "include_24hr_change": "true"
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get(symbol.lower())
        except Exception as e:
            print(f"Error fetching price: {str(e)}")
            return None
    
    @staticmethod
    def get_prices_batch(symbols: List[str]) -> Dict:
        """Obtener múltiples precios"""
        prices = {}
        for symbol in symbols:
            price = TokenService.get_price(symbol)
            if price:
                prices[symbol] = price
        return prices
    
    @staticmethod
    def get_market_data(symbol: str) -> Optional[Dict]:
        """Obtener datos de mercado completos"""
        try:
            url = f"{TokenService.BASE_URL}/coins/{symbol.lower()}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching market data: {str(e)}")
            return None

token_service = TokenService()
