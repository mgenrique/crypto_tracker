"""
Price Fetcher - Crypto Portfolio Tracker v3
===========================================================================

Fetcher centralizado para obtener precios de criptomonedas.
Usa CoinGecko como fuente principal (sin API key).

Características:
- Obtener precios en tiempo real
- Histórico de precios (últimos 90 días)
- Market data (market cap, volume, change)
- Múltiples monedas fiat
- Caché local

Documentación: https://www.coingecko.com/en/api

Author: Crypto Portfolio Tracker Team
Version: 3.0.0
License: MIT
"""

import logging
import requests
import time
from typing import Optional, Dict, Any, List
from decimal import Decimal
from datetime import datetime, timedelta
from functools import lru_cache

from .base_connector import BaseConnector


logger = logging.getLogger(__name__)


class PriceFetcher(BaseConnector):
    """Fetcher centralizado de precios usando CoinGecko."""
    
    name = "price_fetcher"
    version = "1.0"
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    # Mapeo de símbolos a CoinGecko IDs
    COINGECKO_IDS = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "USDC": "usd-coin",
        "USDT": "tether",
        "DAI": "dai",
        "AAVE": "aave",
        "UNI": "uniswap",
        "ARB": "arbitrum",
        "OP": "optimism",
        "SOL": "solana",
        "MATIC": "matic-network",
        "AVAX": "avalanche-2",
        "BASE": "base",
        "LINK": "chainlink",
        "WETH": "ethereum",
        "WBTC": "bitcoin",
        "USDC.e": "usd-coin",
        "USDT.e": "tether",
    }
    
    def __init__(self, timeout: int = 10):
        """
        Inicializa Price Fetcher.
        
        Args:
            timeout: Timeout para requests en segundos
        """
        super().__init__()
        self.timeout = timeout
        self.session = requests.Session()
        self._price_cache: Dict[str, Dict[str, Any]] = {}
        self._cache_timestamp = {}
        self._cache_ttl = 60  # Cache por 60 segundos
    
    def authenticate(self) -> bool:
        """
        Verifica conexión con CoinGecko.
        
        Returns:
            True si conexión exitosa
        """
        try:
            response = self.session.get(
                f"{self.BASE_URL}/ping",
                timeout=self.timeout
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"CoinGecko authentication failed: {e}")
            return False
    
    def get_account_info(self) -> Dict[str, Any]:
        """CoinGecko no tiene "account info"."""
        return {'service': 'coingecko', 'free': True}
    
    def get_balances(self, asset: Optional[str] = None) -> Dict[str, Decimal]:
        """No implementado en Price Fetcher."""
        return {}
    
    def get_transactions(self, asset: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """No implementado en Price Fetcher."""
        return []
    
    def _get_coingecko_id(self, symbol: str) -> Optional[str]:
        """
        Obtiene CoinGecko ID para un símbolo.
        
        Args:
            symbol: Símbolo del token (ej: BTC, ETH)
            
        Returns:
            CoinGecko ID o None
        """
        return self.COINGECKO_IDS.get(symbol.upper())
    
    def _is_cache_valid(self, symbol: str) -> bool:
        """Comprueba si caché es válido."""
        if symbol not in self._cache_timestamp:
            return False
        return time.time() - self._cache_timestamp[symbol] < self._cache_ttl
    
    def get_prices(self, assets: List[str], vs_currency: str = "usd") -> Dict[str, Decimal]:
        """
        Obtiene precios actuales.
        
        Args:
            assets: Lista de símbolos (ej: ['BTC', 'ETH'])
            vs_currency: Moneda de referencia (usd, eur, gbp, etc)
            
        Returns:
            Dict símbolo -> precio
        """
        try:
            prices = {}
            coingecko_ids = []
            symbol_to_id = {}
            
            # Mapear símbolos a IDs y usar caché
            for symbol in assets:
                if self._is_cache_valid(symbol):
                    prices[symbol] = self._price_cache[symbol].get('price', Decimal(0))
                else:
                    cg_id = self._get_coingecko_id(symbol)
                    if cg_id:
                        coingecko_ids.append(cg_id)
                        symbol_to_id[cg_id] = symbol
            
            # Si hay símbolos sin caché, consultar API
            if coingecko_ids:
                response = self.session.get(
                    f"{self.BASE_URL}/simple/price",
                    params={
                        'ids': ','.join(coingecko_ids),
                        'vs_currencies': vs_currency,
                        'include_market_cap': 'true',
                        'include_24hr_vol': 'true',
                        'include_24hr_change': 'true',
                    },
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Procesar resultados
                for cg_id, price_data in data.items():
                    symbol = symbol_to_id.get(cg_id)
                    if symbol:
                        price = Decimal(str(price_data.get(vs_currency, 0)))
                        prices[symbol] = price
                        
                        # Guardar en caché
                        self._price_cache[symbol] = {
                            'price': price,
                            'market_cap': price_data.get(f'{vs_currency}_market_cap'),
                            'volume_24h': price_data.get(f'{vs_currency}_24h_vol'),
                            'change_24h': price_data.get(f'{vs_currency}_24h_change'),
                        }
                        self._cache_timestamp[symbol] = time.time()
            
            logger.debug(f"Got prices for {len(prices)} assets from CoinGecko")
            return prices
        
        except Exception as e:
            logger.error(f"Error getting prices from CoinGecko: {e}")
            return {}
    
    def get_price_history(self, symbol: str, days: int = 30, vs_currency: str = "usd") -> List[Dict]:
        """
        Obtiene histórico de precios.
        
        Args:
            symbol: Símbolo del token
            days: Número de días (máx 90)
            vs_currency: Moneda de referencia
            
        Returns:
            Lista de precios históricos
        """
        try:
            cg_id = self._get_coingecko_id(symbol)
            if not cg_id:
                logger.warning(f"Unknown symbol: {symbol}")
                return []
            
            response = self.session.get(
                f"{self.BASE_URL}/coins/{cg_id}/market_chart",
                params={
                    'vs_currency': vs_currency,
                    'days': min(days, 90),
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            prices = data.get('prices', [])
            
            # Convertir formato
            result = []
            for timestamp, price in prices:
                result.append({
                    'timestamp': datetime.fromtimestamp(timestamp / 1000),
                    'price': Decimal(str(price)),
                })
            
            logger.debug(f"Got {len(result)} price points for {symbol}")
            return result
        
        except Exception as e:
            logger.error(f"Error getting price history: {e}")
            return []
    
    def get_market_data(self, symbol: str, vs_currency: str = "usd") -> Dict[str, Any]:
        """
        Obtiene datos de mercado completos.
        
        Args:
            symbol: Símbolo del token
            vs_currency: Moneda de referencia
            
        Returns:
            Dict con datos de mercado
        """
        try:
            cg_id = self._get_coingecko_id(symbol)
            if not cg_id:
                logger.warning(f"Unknown symbol: {symbol}")
                return {}
            
            response = self.session.get(
                f"{self.BASE_URL}/coins/{cg_id}",
                params={
                    'localization': False,
                    'tickers': False,
                    'market_data': True,
                    'community_data': False,
                    'developer_data': False,
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            market_data = data.get('market_data', {})
            
            return {
                'symbol': symbol,
                'name': data.get('name'),
                'price_usd': Decimal(str(market_data.get(f'current_price', {}).get(vs_currency, 0))),
                'market_cap': market_data.get(f'market_cap', {}).get(vs_currency),
                'volume_24h': market_data.get(f'total_volume', {}).get(vs_currency),
                'change_24h': market_data.get('price_change_percentage_24h'),
                'ath': market_data.get('ath', {}).get(vs_currency),
                'atl': market_data.get('atl', {}).get(vs_currency),
                'rank': data.get('market_cap_rank'),
            }
        
        except Exception as e:
            logger.error(f"Error getting market data: {e}")
            return {}


__all__ = ["PriceFetcher"]
