"""
API Module - Crypto Portfolio Tracker v3
===========================================================================

Módulo de conectores API que incluye:
- BaseConnector (interfaz abstracta)
- BinanceConnector (Binance Exchange)
- CoinbaseConnector (Coinbase Pro)
- KrakenConnector (Kraken Exchange)
- BlockchainConnector (Web3 / EVM chains)
- DeFi Connectors (Uniswap V2/V3, Aave V3)
- PriceFetcher (CoinGecko prices)

Uso:
    from src.api import BinanceConnector, PriceFetcher
    
    # Conectar a Binance
    binance = BinanceConnector(api_key="...", api_secret="...")
    balances = binance.get_balances()
    
    # Obtener precios
    fetcher = PriceFetcher()
    prices = fetcher.get_prices(['BTC', 'ETH'])
"""

from .base_connector import BaseConnector
from .binance_connector import BinanceConnector
from .coinbase_connector import CoinbaseConnector
from .kraken_connector import KrakenConnector
from .blockchain_connector import BlockchainConnector
from .defi_connectors import (
    UniswapV2Connector,
    UniswapV3Connector,
    AaveV3Connector,
)
from .price_fetcher import PriceFetcher

__all__ = [
    # Base
    "BaseConnector",
    # Exchange Connectors
    "BinanceConnector",
    "CoinbaseConnector",
    "KrakenConnector",
    # Blockchain & Web3
    "BlockchainConnector",
    # DeFi Connectors
    "UniswapV2Connector",
    "UniswapV3Connector",
    "AaveV3Connector",
    # Price Fetcher
    "PriceFetcher",
]
