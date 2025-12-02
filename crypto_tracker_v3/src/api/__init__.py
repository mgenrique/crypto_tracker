"""
External API Connectors
=======================

Conectores para exchanges y blockchains.

Módulos:
- base_connector: Clase base para conectores
- binance_connector: Conector Binance
- blockchain_connector: Conector Blockchain (Web3)
- coinbase_connector: Conector Coinbase
- kraken_connector: Conector Kraken
- defi_connectors: Conectores DeFi (Uniswap, Aave)
- price_fetcher: Obtención de precios
"""

from .base_connector import BaseConnector
from .price_fetcher import PriceFetcher

__all__ = [
    "BaseConnector",
    "PriceFetcher",
]
