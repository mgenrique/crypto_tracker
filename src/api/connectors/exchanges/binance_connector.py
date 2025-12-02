# src/api/connectors/exchanges/binance_connector.py

"""
Binance Exchange Connector
===========================

Real-time integration with Binance API.
Completa con todas las funcionalidades.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from decimal import Decimal
from datetime import datetime, timedelta
import time

try:
    from binance.client import Client as BinanceClient
    from binance.exceptions import BinanceAPIException, BinanceOrderException
except ImportError:
    BinanceClient = None
    BinanceAPIException = None
    BinanceOrderException = None

logger = logging.getLogger(__name__)


class BinanceConnector:
    """Binance exchange connector - COMPLETO"""
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        """
        Initialize Binance connector
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            testnet: Use testnet (default: False)
        """
        if not BinanceClient:
            raise ImportError("python-binance not installed. pip install python-binance")
        
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        
        if testnet:
            self.client = BinanceClient(
                api_key=api_key,
                api_secret=api_secret,
                testnet=True
            )
        else:
            self.client = BinanceClient(api_key=api_key, api_secret=api_secret)
        
        self.logger = logging.getLogger(f"connector.binance.{api_key[:8]}")
    
    async def validate_connection(self) -> bool:
        """Validate Binance connection"""
        try:
            self.client.get_account()
            self.logger.info("✅ Binance connection validated")
            return True
        except BinanceAP
