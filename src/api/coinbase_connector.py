"""
Coinbase Connector - Crypto Portfolio Tracker v3
===========================================================================

Conector para API de Coinbase Pro.
Soporta:
- Obtener saldos y balances
- Histórico de transacciones
- Precios en tiempo real
- Información de cuenta

Documentación: https://docs.cloud.coinbase.com/exchange/reference

Author: Crypto Portfolio Tracker Team
Version: 3.0.0
License: MIT
"""

import logging
import hashlib
import hmac
import base64
import time
from typing import Optional, Dict, Any, List
from decimal import Decimal
import requests

from .base_connector import BaseConnector


logger = logging.getLogger(__name__)


class CoinbaseConnector(BaseConnector):
    """Conector para API de Coinbase Pro."""
    
    name = "coinbase"
    version = "1.0"
    
    BASE_URL = "https://api.exchange.coinbase.com"
    
    def __init__(self, api_key: str, api_secret: str, passphrase: str):
        """
        Inicializa conector de Coinbase.
        
        Args:
            api_key: Coinbase API key
            api_secret: Coinbase API secret
            passphrase: Coinbase passphrase
        """
        super().__init__(api_key, api_secret)
        self.passphrase = passphrase
        self.session = requests.Session()
    
    def _generate_auth(self, method: str, request_path: str, body: str = "") -> Dict[str, str]:
        """
        Genera headers de autenticación para Coinbase.
        
        Args:
            method: GET, POST, DELETE, etc
            request_path: Ruta del endpoint
            body: Body de la request (si existe)
            
        Returns:
            Dict con headers de autenticación
        """
        timestamp = str(time.time())
        message = timestamp + method + request_path + body
        message_bytes = message.encode('ascii')
        hmac_key = base64.b64decode(self.api_secret)
        signature = hmac.new(hmac_key, message_bytes, hashlib.sha256)
        signature_b64 = base64.b64encode(signature.digest()).decode('utf-8')
        
        return {
            'CB-ACCESS-SIGN': signature_b64,
            'CB-ACCESS-TIMESTAMP': timestamp,
            'CB-ACCESS-KEY': self.api_key,
            'CB-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
    
    def authenticate(self) -> bool:
        """
        Verifica conexión con Coinbase.
        
        Returns:
            True si conexión exitosa
        """
        try:
            headers = self._generate_auth('GET', '/users/self')
            response = self.session.get(
                f"{self.BASE_URL}/users/self",
                headers=headers
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Coinbase authentication failed: {e}")
            return False
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Obtiene información de la cuenta.
        
        Returns:
            Dict con datos de cuenta
        """
        try:
            headers = self._generate_auth('GET', '/accounts')
            response = self.session.get(
                f"{self.BASE_URL}/accounts",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting Coinbase account info: {e}")
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
            headers = self._generate_auth('GET', '/accounts')
            response = self.session.get(
                f"{self.BASE_URL}/accounts",
                headers=headers
            )
            response.raise_for_status()
            
            accounts = response.json()
            balances = {}
            
            for account in accounts:
                symbol = account['currency']
                balance = Decimal(account['balance'])
                
                if balance > 0:  # Solo incluir si hay saldo
                    if asset and symbol != asset:
                        continue
                    balances[symbol] = balance
            
            logger.debug(f"Got {len(balances)} balances from Coinbase")
            return balances
        
        except Exception as e:
            logger.error(f"Error getting Coinbase balances: {e}")
            return {}
    
    def get_transactions(self, asset: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        Obtiene histórico de transacciones.
        
        Args:
            asset: Activo específico (opcional)
            limit: Límite de registros
            
        Returns:
            Lista de transacciones
        """
        try:
            # Obtener cuentas primero
            headers = self._generate_auth('GET', '/accounts')
            response = self.session.get(
                f"{self.BASE_URL}/accounts",
                headers=headers
            )
            response.raise_for_status()
            accounts = response.json()
            
            transactions = []
            
            # Para cada cuenta, obtener el histórico
            for account in accounts:
                if asset and account['currency'] != asset:
                    continue
                
                account_id = account['id']
                headers = self._generate_auth('GET', f'/accounts/{account_id}/ledger')
                response = self.session.get(
                    f"{self.BASE_URL}/accounts/{account_id}/ledger",
                    headers=headers,
                    params={'limit': limit}
                )
                response.raise_for_status()
                
                for entry in response.json():
                    transactions.append({
                        'type': entry['type'],  # deposit, withdrawal, trade, etc
                        'asset': account['currency'],
                        'amount': Decimal(entry['amount']),
                        'balance': Decimal(entry['balance']),
                        'timestamp': entry['created_at'],
                        'description': entry.get('description', '')
                    })
            
            logger.debug(f"Got {len(transactions)} transactions from Coinbase")
            return sorted(transactions, key=lambda x: x['timestamp'], reverse=True)
        
        except Exception as e:
            logger.error(f"Error getting Coinbase transactions: {e}")
            return []
    
    def get_prices(self, assets: List[str]) -> Dict[str, Decimal]:
        """
        Obtiene precios en USD.
        
        Args:
            assets: Lista de símbolos (ej: ['BTC', 'ETH'])
            
        Returns:
            Dict símbolo -> precio USD
        """
        try:
            prices = {}
            
            for asset in assets:
                product_id = f"{asset}-USD"
                headers = self._generate_auth('GET', f'/products/{product_id}/ticker')
                response = self.session.get(
                    f"{self.BASE_URL}/products/{product_id}/ticker",
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    prices[asset] = Decimal(data['price'])
                else:
                    logger.warning(f"Could not get price for {asset}")
            
            return prices
        
        except Exception as e:
            logger.error(f"Error getting Coinbase prices: {e}")
            return {}


__all__ = ["CoinbaseConnector"]
