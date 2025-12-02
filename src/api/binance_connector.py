"""
Binance Connector - Crypto Portfolio Tracker v3
===========================================================================

Conector para API de Binance.
Soporta:
- Obtener saldos y balances
- Histórico de transacciones
- Precios en tiempo real
- Información de cuenta

Documentación: https://binance-docs.github.io/apidocs/

Author: Crypto Portfolio Tracker Team
Version: 3.0.0
License: MIT
"""

import logging
import hashlib
import hmac
import time
from typing import Optional, Dict, Any, List
from decimal import Decimal
import requests

from .base_connector import BaseConnector


logger = logging.getLogger(__name__)


class BinanceConnector(BaseConnector):
    """Conector para API de Binance."""
    
    name = "binance"
    version = "1.0"
    
    BASE_URL = "https://api.binance.com"
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        """
        Inicializa conector de Binance.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            testnet: Usar testnet (default: False)
        """
        super().__init__(api_key, api_secret)
        self.base_url = self.BASE_URL
        self.testnet = testnet
        if testnet:
            self.base_url = "https://testnet.binance.vision"
        
        self.session = requests.Session()
        self.session.headers.update({
            'X-MBX-APIKEY': self.api_key
        })
    
    def _generate_signature(self, data: Dict[str, Any]) -> str:
        """
        Genera firma HMAC para requests autenticadas.
        
        Args:
            data: Parámetros de la request
            
        Returns:
            Firma HMAC SHA256
        """
        query_string = '&'.join([f"{k}={v}" for k, v in data.items()])
        signature = hmac.new(
            self.api_secret.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def authenticate(self) -> bool:
        """
        Verifica conexión con Binance.
        
        Returns:
            True si conexión exitosa
        """
        try:
            response = self.session.get(f"{self.base_url}/api/v3/ping")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Binance authentication failed: {e}")
            return False
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Obtiene información de la cuenta.
        
        Returns:
            Dict con datos de cuenta
        """
        try:
            timestamp = int(time.time() * 1000)
            params = {'timestamp': timestamp}
            params['signature'] = self._generate_signature(params)
            
            response = self.session.get(
                f"{self.base_url}/api/v3/account",
                params=params
            )
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            logger.error(f"Error getting Binance account info: {e}")
            return {}
    
    def get_balances(self, asset: Optional[str] = None) -> Dict[str, Decimal]:
        """
        Obtiene saldos.
        
        Args:
            asset: Activo específico (opcional)
            
        Returns:
            Dict símbolo -> saldo
        """
        try:
            account_info = self.get_account_info()
            balances = {}
            
            for balance in account_info.get('balances', []):
                symbol = balance['asset']
                free = Decimal(balance['free'])
                locked = Decimal(balance['locked'])
                total = free + locked
                
                if total > 0:  # Solo incluir si hay saldo
                    if asset and symbol != asset:
                        continue
                    balances[symbol] = total
            
            logger.debug(f"Got {len(balances)} balances from Binance")
            return balances
        
        except Exception as e:
            logger.error(f"Error getting Binance balances: {e}")
            return {}
    
    def get_transactions(self, asset: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        Obtiene histórico de depósitos y retiros.
        
        Args:
            asset: Activo específico (opcional)
            limit: Límite de registros
            
        Returns:
            Lista de transacciones
        """
        try:
            timestamp = int(time.time() * 1000)
            params = {
                'timestamp': timestamp,
                'limit': limit
            }
            params['signature'] = self._generate_signature(params)
            
            # Depósitos
            deposits_response = self.session.get(
                f"{self.base_url}/wapi/v3/depositHistory.html",
                params=params
            )
            deposits_response.raise_for_status()
            deposits = deposits_response.json().get('depositList', [])
            
            # Retiros
            withdraws_response = self.session.get(
                f"{self.base_url}/wapi/v3/withdrawHistory.html",
                params=params
            )
            withdraws_response.raise_for_status()
            withdraws = withdraws_response.json().get('withdrawList', [])
            
            transactions = []
            
            # Procesar depósitos
            for tx in deposits:
                if asset and tx['coin'] != asset:
                    continue
                transactions.append({
                    'type': 'deposit',
                    'asset': tx['coin'],
                    'amount': Decimal(tx['amount']),
                    'timestamp': tx['insertTime'],
                    'status': tx['status'],
                    'txid': tx.get('txId', '')
                })
            
            # Procesar retiros
            for tx in withdraws:
                if asset and tx['coin'] != asset:
                    continue
                transactions.append({
                    'type': 'withdrawal',
                    'asset': tx['coin'],
                    'amount': Decimal(tx['amount']),
                    'fee': Decimal(tx.get('transactionFee', 0)),
                    'timestamp': tx['applyTime'],
                    'status': tx['status'],
                    'txid': tx.get('txId', '')
                })
            
            logger.debug(f"Got {len(transactions)} transactions from Binance")
            return sorted(transactions, key=lambda x: x['timestamp'], reverse=True)
        
        except Exception as e:
            logger.error(f"Error getting Binance transactions: {e}")
            return []
    
    def get_prices(self, assets: List[str]) -> Dict[str, Decimal]:
        """
        Obtiene precios en USDT.
        
        Args:
            assets: Lista de símbolos (ej: ['BTC', 'ETH'])
            
        Returns:
            Dict símbolo -> precio USD
        """
        try:
            prices = {}
            
            for asset in assets:
                symbol = f"{asset}USDT"
                response = self.session.get(
                    f"{self.base_url}/api/v3/ticker/price",
                    params={'symbol': symbol}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    prices[asset] = Decimal(data['price'])
                else:
                    logger.warning(f"Could not get price for {asset}")
            
            return prices
        
        except Exception as e:
            logger.error(f"Error getting Binance prices: {e}")
            return {}


__all__ = ["BinanceConnector"]
