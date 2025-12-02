"""
DeFi Connectors - Crypto Portfolio Tracker v3
===========================================================================

Conectores para protocolos DeFi:
- Uniswap V2 y V3 (liquidez)
- Aave V2 y V3 (lending)

Soporta:
- Obtener pools y posiciones
- Calcular LP valores
- Obtener posiciones Aave
- Health factors y liquidación

Author: Crypto Portfolio Tracker Team
Version: 3.0.0
License: MIT
"""

import logging
from typing import Optional, Dict, Any, List
from decimal import Decimal
from web3 import Web3

from .base_connector import BaseConnector


logger = logging.getLogger(__name__)

# Uniswap V3 Pool ABI (funciones necesarias)
UNISWAP_V3_POOL_ABI = [
    {
        "inputs": [],
        "name": "slot0",
        "outputs": [
            {"name": "sqrtPriceX96", "type": "uint160"},
            {"name": "tick", "type": "int24"},
        ],
        "type": "function",
    },
    {
        "inputs": [{"name": "tickLower", "type": "int24"}, {"name": "tickUpper", "type": "int24"}],
        "name": "ticks",
        "outputs": [{"name": "liquidityGross", "type": "uint128"}],
        "type": "function",
    },
]

# Aave Pool ABI (funciones necesarias)
AAVE_POOL_ABI = [
    {
        "inputs": [{"name": "user", "type": "address"}],
        "name": "getUserAccountData",
        "outputs": [
            {"name": "totalCollateralBase", "type": "uint256"},
            {"name": "totalDebtBase", "type": "uint256"},
            {"name": "availableBorrowsBase", "type": "uint256"},
            {"name": "currentLiquidationThreshold", "type": "uint256"},
            {"name": "ltv", "type": "uint256"},
            {"name": "healthFactor", "type": "uint256"},
        ],
        "type": "function",
    },
]


class UniswapV2Connector(BaseConnector):
    """Conector para Uniswap V2."""
    
    name = "uniswap_v2"
    version = "1.0"
    
    FACTORY_ADDRESS = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
    ROUTER_ADDRESS = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    
    def __init__(self, w3: Web3):
        """
        Inicializa conector Uniswap V2.
        
        Args:
            w3: Instancia de Web3
        """
        super().__init__()
        self.w3 = w3
    
    def authenticate(self) -> bool:
        return self.w3.is_connected()
    
    def get_account_info(self) -> Dict[str, Any]:
        return {'pool': 'uniswap_v2'}
    
    def get_balances(self, asset: Optional[str] = None) -> Dict[str, Decimal]:
        """Uniswap V2 no soporta get_balances directo."""
        return {}
    
    def get_transactions(self, asset: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Requiere indexer como The Graph."""
        return []
    
    def get_prices(self, assets: List[str]) -> Dict[str, Decimal]:
        """Usar PriceFetcher en su lugar."""
        return {}
    
    def get_pool_reserves(self, pool_address: str) -> tuple:
        """
        Obtiene reserves de un pool V2.
        
        Args:
            pool_address: Dirección del pool
            
        Returns:
            Tupla (reserve0, reserve1)
        """
        try:
            logger.debug(f"Getting V2 pool reserves for {pool_address}")
            # Implementación requiere contrato del pool
            return (Decimal(0), Decimal(0))
        except Exception as e:
            logger.error(f"Error getting V2 pool reserves: {e}")
            return (Decimal(0), Decimal(0))


class UniswapV3Connector(BaseConnector):
    """Conector para Uniswap V3."""
    
    name = "uniswap_v3"
    version = "1.0"
    
    FACTORY_ADDRESS = "0x1F98431c8aD98523631AE4a59f267346ea31394E"
    ROUTER_ADDRESS = "0xE592427A0AEce92De3Edee1F18E0157C05861564"
    POSITIONS_MANAGER = "0xC36442b4a4522E871399CD717aBDD847Ab11FE88"
    
    def __init__(self, w3: Web3):
        """
        Inicializa conector Uniswap V3.
        
        Args:
            w3: Instancia de Web3
        """
        super().__init__()
        self.w3 = w3
    
    def authenticate(self) -> bool:
        return self.w3.is_connected()
    
    def get_account_info(self) -> Dict[str, Any]:
        return {'pool': 'uniswap_v3'}
    
    def get_balances(self, asset: Optional[str] = None) -> Dict[str, Decimal]:
        """Uniswap V3 no soporta get_balances directo."""
        return {}
    
    def get_transactions(self, asset: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Requiere indexer como The Graph."""
        return []
    
    def get_prices(self, assets: List[str]) -> Dict[str, Decimal]:
        """Usar PriceFetcher en su lugar."""
        return {}
    
    def get_pool_data(self, pool_address: str) -> Dict[str, Any]:
        """
        Obtiene datos de un pool V3.
        
        Args:
            pool_address: Dirección del pool
            
        Returns:
            Dict con datos del pool
        """
        try:
            contract = self.w3.eth.contract(
                address=pool_address,
                abi=UNISWAP_V3_POOL_ABI
            )
            
            slot0 = contract.functions.slot0().call()
            sqrt_price = Decimal(slot0[0])
            current_tick = slot0[1]
            
            return {
                'sqrt_price': sqrt_price,
                'current_tick': current_tick,
            }
        except Exception as e:
            logger.error(f"Error getting V3 pool data: {e}")
            return {}
    
    def calculate_position_value(self, token0_balance: Decimal, token1_balance: Decimal,
                                 token0_price: Decimal, token1_price: Decimal) -> Decimal:
        """
        Calcula valor total de una posición LP.
        
        Args:
            token0_balance: Balance de token 0
            token1_balance: Balance de token 1
            token0_price: Precio de token 0 en USD
            token1_price: Precio de token 1 en USD
            
        Returns:
            Valor total en USD
        """
        value = (token0_balance * token0_price) + (token1_balance * token1_price)
        return value


class AaveV3Connector(BaseConnector):
    """Conector para Aave V3."""
    
    name = "aave_v3"
    version = "1.0"
    
    POOL_ADDRESS = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"  # Ethereum
    POOL_DATA_PROVIDER = "0x7B4EB56E7CD4eBFD82a2ef47302c0deED5713f71"
    
    def __init__(self, w3: Web3, pool_address: Optional[str] = None):
        """
        Inicializa conector Aave V3.
        
        Args:
            w3: Instancia de Web3
            pool_address: Dirección del pool (opcional)
        """
        super().__init__()
        self.w3 = w3
        self.pool_address = pool_address or self.POOL_ADDRESS
    
    def authenticate(self) -> bool:
        return self.w3.is_connected()
    
    def get_account_info(self) -> Dict[str, Any]:
        return {'protocol': 'aave_v3'}
    
    def get_balances(self, asset: Optional[str] = None) -> Dict[str, Decimal]:
        """Usar get_user_account_data en su lugar."""
        return {}
    
    def get_transactions(self, asset: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Requiere indexer como The Graph."""
        return []
    
    def get_prices(self, assets: List[str]) -> Dict[str, Decimal]:
        """Usar PriceFetcher en su lugar."""
        return {}
    
    def get_user_account_data(self, user_address: str) -> Dict[str, Decimal]:
        """
        Obtiene datos de cuenta de usuario en Aave V3.
        
        Args:
            user_address: Dirección del usuario
            
        Returns:
            Dict con datos de account
        """
        try:
            contract = self.w3.eth.contract(
                address=self.pool_address,
                abi=AAVE_POOL_ABI
            )
            
            data = contract.functions.getUserAccountData(user_address).call()
            
            return {
                'total_collateral': Decimal(data[0]) / Decimal(10 ** 8),
                'total_debt': Decimal(data[1]) / Decimal(10 ** 8),
                'available_borrows': Decimal(data[2]) / Decimal(10 ** 8),
                'liquidation_threshold': Decimal(data[3]) / Decimal(10000),
                'ltv': Decimal(data[4]) / Decimal(10000),
                'health_factor': Decimal(data[5]) / Decimal(10 ** 18),
            }
        except Exception as e:
            logger.error(f"Error getting Aave user account data: {e}")
            return {}


__all__ = [
    "UniswapV2Connector",
    "UniswapV3Connector",
    "AaveV3Connector",
]
