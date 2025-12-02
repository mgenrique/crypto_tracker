"""
Binance Real Connector
======================

Real Binance API integration for fetching account data.
"""

from binance.client import Client
from binance.exceptions import BinanceAPIException
from decimal import Decimal
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class BinanceRealConnector:
    """Real Binance API connector"""

    def __init__(self, api_key: str, api_secret: str):
        """
        Initialize Binance connector
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.client = Client(api_key, api_secret)
        self.logger = logging.getLogger(f"connector.binance.{api_key[:8]}")

    def validate_connection(self) -> bool:
        """Validate Binance API connection"""
        try:
            self.client.get_account()
            self.logger.info("✅ Binance connection validated")
            return True
        except BinanceAPIException as e:
            self.logger.error(f"❌ Binance API error: {str(e)}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Connection error: {str(e)}")
            return False

    def get_balance(self) -> Dict[str, Dict[str, Any]]:
        """
        Get account balance from Binance
        
        Returns:
            Dict with token balances
            {
                "BTC": {"free": "0.5", "locked": "0.1"},
                "ETH": {"free": "10.0", "locked": "0.0"},
                ...
            }
        """
        try:
            account = self.client.get_account()
            balances = {}
            
            for balance in account['balances']:
                token = balance['asset']
                free = Decimal(balance['free'])
                locked = Decimal(balance['locked'])
                
                # Only include non-zero balances
                total = free + locked
                if total > 0:
                    balances[token] = {
                        "free": str(free),
                        "locked": str(locked),
                        "total": str(total)
                    }
            
            self.logger.info(f"✅ Balance fetched: {len(balances)} assets")
            return balances
        except BinanceAPIException as e:
            self.logger.error(f"❌ Error fetching balance: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"❌ Error fetching balance: {str(e)}")
            raise

    def get_asset_balance(self, asset: str) -> Optional[Dict[str, str]]:
        """Get balance for specific asset"""
        try:
            account = self.client.get_account()
            
            for balance in account['balances']:
                if balance['asset'] == asset:
                    return {
                        "free": balance['free'],
                        "locked": balance['locked'],
                        "total": str(Decimal(balance['free']) + Decimal(balance['locked']))
                    }
            
            return None
        except Exception as e:
            self.logger.error(f"❌ Error fetching {asset} balance: {str(e)}")
            return None

    def get_trading_fees(self) -> Dict[str, Any]:
        """Get trading fees"""
        try:
            fees = self.client.get_trade_fee()
            return fees
        except Exception as e:
            self.logger.error(f"❌ Error fetching fees: {str(e)}")
            raise

    def get_deposit_address(self, coin: str, network: str = "BTC") -> Optional[str]:
        """Get deposit address for coin"""
        try:
            address = self.client.get_deposit_address(coin=coin, network=network)
            return address.get('address')
        except Exception as e:
            self.logger.error(f"❌ Error getting deposit address: {str(e)}")
            return None

    def get_withdraw_history(self, coin: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get withdrawal history"""
        try:
            params = {"limit": limit}
            if coin:
                params["coin"] = coin
            
            history = self.client.get_withdraw_history(**params)
            
            return [
                {
                    "id": tx['id'],
                    "coin": tx['coin'],
                    "amount": tx['amount'],
                    "address": tx['address'],
                    "status": tx['status'],
                    "timestamp": datetime.fromtimestamp(tx['applyTime'] / 1000).isoformat(),
                    "txid": tx.get('txId')
                }
                for tx in history
            ]
        except Exception as e:
            self.logger.error(f"❌ Error fetching withdraw history: {str(e)}")
            return []

    def get_deposit_history(self, coin: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get deposit history"""
        try:
            params = {"limit": limit}
            if coin:
                params["coin"] = coin
            
            history = self.client.get_deposit_history(**params)
            
            return [
                {
                    "id": tx['id'],
                    "coin": tx['coin'],
                    "amount": tx['amount'],
                    "address": tx['address'],
                    "status": tx['status'],
                    "timestamp": datetime.fromtimestamp(tx['insertTime'] / 1000).isoformat(),
                    "txid": tx.get('txId')
                }
                for tx in history
            ]
        except Exception as e:
            self.logger.error(f"❌ Error fetching deposit history: {str(e)}")
            return []

    def get_trades(self, symbol: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get trades for symbol
        
        Args:
            symbol: Trading pair (e.g., 'ETHUSDT')
            limit: Number of trades to fetch
            
        Returns:
            List of trades
        """
        try:
            trades = self.client.get_my_trades(symbol=symbol, limit=limit)
            
            return [
                {
                    "id": t['id'],
                    "symbol": t['symbol'],
                    "price": t['price'],
                    "qty": t['qty'],
                    "commission": t['commission'],
                    "commissionAsset": t['commissionAsset'],
                    "is_buyer": t['isBuyer'],
                    "is_maker": t['isMaker'],
                    "timestamp": datetime.fromtimestamp(t['time'] / 1000).isoformat()
                }
                for t in trades
            ]
        except Exception as e:
            self.logger.error(f"❌ Error fetching trades: {str(e)}")
            return []

    def get_all_trades(self) -> List[Dict[str, Any]]:
        """Get all trades across all symbols"""
        try:
            # Get all trading pairs
            exchange_info = self.client.get_exchange_info()
            symbols = [s['symbol'] for s in exchange_info['symbols']]
            
            all_trades = []
            for symbol in symbols:
                try:
                    trades = self.get_trades(symbol, limit=10)
                    all_trades.extend(trades)
                except:
                    pass  # Skip symbols with no trades
            
            # Sort by timestamp
            all_trades.sort(key=lambda x: x['timestamp'], reverse=True)
            
            self.logger.info(f"✅ Fetched {len(all_trades)} trades")
            return all_trades
        except Exception as e:
            self.logger.error(f"❌ Error fetching all trades: {str(e)}")
            return []

    def get_price(self, symbol: str) -> Optional[str]:
        """Get current price for symbol"""
        try:
            price = self.client.get_symbol_info(symbol)
            # Use ticker instead
            ticker = self.client.get_ticker(symbol=symbol)
            return ticker['lastPrice']
        except Exception as e:
            self.logger.error(f"❌ Error fetching price: {str(e)}")
            return None

    def get_all_prices(self) -> Dict[str, str]:
        """Get all trading pair prices"""
        try:
            prices = self.client.get_all_tickers()
            return {p['symbol']: p['price'] for p in prices}
        except Exception as e:
            self.logger.error(f"❌ Error fetching prices: {str(e)}")
            return {}
