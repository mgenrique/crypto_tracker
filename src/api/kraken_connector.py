"""
Kraken Connector - Crypto Portfolio Tracker v3
===========================================================================

Conector para API de Kraken.
Soporta:
- Obtener saldos y balances
- Histórico de transacciones
- Precios en tiempo real
- Información de cuenta

Documentación: https://docs.kraken.com/rest/

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
from urllib.parse import urlencode
import requests

from .base_connector import BaseConnector


logger = logging.getLogger(__name__)


class KrakenConnector(BaseConnector):
    """Conector para API de Kraken."""
    
    name = "kraken"
    version = "1.0"
    
    BASE_URL = "https://api.kraken.com"
    API_VERSION = "0"
    
    def __init__(self, api_key: str, api_secret: str):
        """
        Inicializa conector de Kraken.
        
        Args:
            api_key: Kraken API key
            api_secret: Kraken API secret
        """
        super().__init__(api_key, api_secret)
        self.session = requests.Session()
    
    def _generate_signature(self, urlpath: str, data: Dict[str, Any], nonce: str) -> str:
        """
        Genera firma para requests autenticadas a Kraken.
        
        Args:
            urlpath: Ruta del endpoint (ej: /0/private/Balance)
            data: Parámetros de la request
            nonce: Nonce (timestamp)
            
        Returns:
            Firma base64
        """
        postdata = urlencode(data)
        encoded = (str(nonce) + postdata).encode()
        message = urlpath.encode() + hashlib.sha256(encoded).digest()
        
        signature = hmac.new(
            base64.b64decode(self.api_secret),
            message,
            hashlib.sha512
        )
        signature_b64 = base64.b64encode(signature.digest()).decode()
        return signature_b64
    
    def _get_kraken_timestamp(self) -> int:
        """Obtiene timestamp en formato Kraken (segundos desde epoch)."""
        return int(time.time())
    
    def authenticate(self) -> bool:
        """
        Verifica conexión con Kraken.
        
        Returns:
            True si conexión exitosa
        """
        try:
            nonce = str(int(time.time() * 1000))
            data = {'nonce': nonce}
            
            signature = self._generate_signature('/0/private/Balance', data, nonce)
            
            headers = {
                'API-Sign': signature,
                'API-Key': self.api_key
            }
            
            response = self.session.post(
                f"{self.BASE_URL}/0/private/Balance",
                headers=headers,
                data=data
            )
            
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Kraken authentication failed: {e}")
            return False
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Obtiene información de la cuenta.
        
        Returns:
            Dict con datos de cuenta
        """
        try:
            nonce = str(int(time.time() * 1000))
            data = {'nonce': nonce}
            signature = self._generate_signature('/0/private/QueryUserData', data, nonce)
            
            headers = {
                'API-Sign': signature,
                'API-Key': self.api_key
            }
            
            response = self.session.post(
                f"{self.BASE_URL}/0/private/QueryUserData",
                headers=headers,
                data=data
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get('error'):
                logger.error(f"Kraken error: {result['error']}")
                return {}
            
            return result.get('result', {})
        
        except Exception as e:
            logger.error(f"Error getting Kraken account info: {e}")
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
            nonce = str(int(time.time() * 1000))
            data = {'nonce': nonce}
            signature = self._generate_signature('/0/private/Balance', data, nonce)
            
            headers = {
                'API-Sign': signature,
                'API-Key': self.api_key
            }
            
            response = self.session.post(
                f"{self.BASE_URL}/0/private/Balance",
                headers=headers,
                data=data
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get('error'):
                logger.error(f"Kraken error: {result['error']}")
                return {}
            
            balances = {}
            for symbol, balance in result.get('result', {}).items():
                # Kraken usa prefijos como X para crypto y Z para fiat
                clean_symbol = symbol.lstrip('XZ')
                balance_decimal = Decimal(balance)
                
                if balance_decimal > 0:
                    if asset and clean_symbol != asset:
                        continue
                    balances[clean_symbol] = balance_decimal
            
            logger.debug(f"Got {len(balances)} balances from Kraken")
            return balances
        
        except Exception as e:
            logger.error(f"Error getting Kraken balances: {e}")
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
            nonce = str(int(time.time() * 1000))
            data = {
                'nonce': nonce,
                'trades': True
            }
            signature = self._generate_signature('/0/private/TradesHistory', data, nonce)
            
            headers = {
                'API-Sign': signature,
                'API-Key': self.api_key
            }
            
            response = self.session.post(
                f"{self.BASE_URL}/0/private/TradesHistory",
                headers=headers,
                data=data
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get('error'):
                logger.error(f"Kraken error: {result['error']}")
                return []
            
            transactions = []
            for tx_id, tx_data in result.get('result', {}).items():
                transactions.append({
                    'txid': tx_id,
                    'type': 'trade',
                    'pair': tx_data.get('pair'),
                    'amount': Decimal(tx_data.get('cost', 0)),
                    'fee': Decimal(tx_data.get('fee', 0)),
                    'timestamp': tx_data.get('time'),
                })
            
            logger.debug(f"Got {len(transactions)} transactions from Kraken")
            return sorted(transactions, key=lambda x: x['timestamp'], reverse=True)[:limit]
        
        except Exception as e:
            logger.error(f"Error getting Kraken transactions: {e}")
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
                pair = f"{asset}USD"
                response = self.session.get(
                    f"{self.BASE_URL}/0/public/Ticker",
                    params={'pair': pair}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if not result.get('error'):
                        ticker_data = result['result']
                        # Kraken retorna una llave con el par
                        for key, value in ticker_data.items():
                            prices[asset] = Decimal(value['c'][0])  # c = last trade closed
                else:
                    logger.warning(f"Could not get price for {asset}")
            
            return prices
        
        except Exception as e:
            logger.error(f"Error getting Kraken prices: {e}")
            return {}


__all__ = ["KrakenConnector"]
