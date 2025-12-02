"""
Blockchain Connector - Crypto Portfolio Tracker v3
===========================================================================

Conector para interactuar directamente con blockchains usando Web3.py
Soporta:
- Obtener saldos de ERC-20 tokens
- Leer datos de smart contracts
- Histórico de transacciones on-chain
- Múltiples redes EVM

Redes soportadas:
- Ethereum
- Arbitrum
- Base
- Polygon
- Optimism
- Avalanche

Author: Crypto Portfolio Tracker Team
Version: 3.0.0
License: MIT
"""

import logging
from typing import Optional, Dict, Any, List
from decimal import Decimal
from web3 import Web3
from web3.contract import Contract

from .base_connector import BaseConnector


logger = logging.getLogger(__name__)

# ERC-20 ABI (funciones necesarias)
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function",
    },
]


class BlockchainConnector(BaseConnector):
    """Conector para blockchains EVM usando Web3.py."""
    
    name = "blockchain"
    version = "1.0"
    
    # RPC endpoints por red
    RPC_ENDPOINTS = {
        "ethereum": "https://eth.infura.io/v3/YOUR_INFURA_KEY",
        "arbitrum": "https://arb1.arbitrum.io/rpc",
        "base": "https://mainnet.base.org",
        "polygon": "https://polygon-rpc.com",
        "optimism": "https://mainnet.optimism.io",
        "avalanche": "https://api.avax.network/ext/bc/C/rpc",
    }
    
    def __init__(self, network: str = "ethereum", rpc_url: Optional[str] = None):
        """
        Inicializa conector blockchain.
        
        Args:
            network: Red blockchain (ethereum, arbitrum, base, etc)
            rpc_url: URL RPC personalizada (opcional)
        """
        super().__init__()
        self.network = network
        
        # Usar RPC personalizado o default
        endpoint = rpc_url or self.RPC_ENDPOINTS.get(network)
        if not endpoint:
            raise ValueError(f"Unknown network: {network}")
        
        self.w3 = Web3(Web3.HTTPProvider(endpoint))
        
        if not self.w3.is_connected():
            logger.error(f"Could not connect to {network} RPC")
        else:
            logger.info(f"Connected to {network} blockchain")
    
    def authenticate(self) -> bool:
        """
        Verifica conexión con blockchain.
        
        Returns:
            True si conectado
        """
        try:
            return self.w3.is_connected()
        except Exception as e:
            logger.error(f"Blockchain authentication failed: {e}")
            return False
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Obtiene información de bloque actual.
        
        Returns:
            Dict con info de red
        """
        try:
            block = self.w3.eth.get_block('latest')
            return {
                'network': self.network,
                'block_number': block['number'],
                'block_timestamp': block['timestamp'],
                'chain_id': self.w3.eth.chain_id,
            }
        except Exception as e:
            logger.error(f"Error getting blockchain info: {e}")
            return {}
    
    def get_balances(self, wallet_address: str, tokens: Optional[List[str]] = None) -> Dict[str, Decimal]:
        """
        Obtiene saldos de tokens ERC-20.
        
        Args:
            wallet_address: Dirección de wallet (0x...)
            tokens: Lista de direcciones de contratos (opcional)
            
        Returns:
            Dict símbolo -> saldo
        """
        try:
            balances = {}
            
            # ETH nativo
            eth_balance = self.w3.eth.get_balance(wallet_address)
            balances['ETH'] = Decimal(eth_balance) / Decimal(10 ** 18)
            
            # Tokens ERC-20
            if tokens:
                for token_address in tokens:
                    try:
                        contract = self.w3.eth.contract(
                            address=token_address,
                            abi=ERC20_ABI
                        )
                        
                        # Obtener símbolo y decimales
                        symbol = contract.functions.symbol().call()
                        decimals = contract.functions.decimals().call()
                        
                        # Obtener balance
                        balance_raw = contract.functions.balanceOf(wallet_address).call()
                        balance = Decimal(balance_raw) / Decimal(10 ** decimals)
                        
                        if balance > 0:
                            balances[symbol] = balance
                    
                    except Exception as e:
                        logger.warning(f"Could not get balance for token {token_address}: {e}")
            
            logger.debug(f"Got {len(balances)} balances from {self.network}")
            return balances
        
        except Exception as e:
            logger.error(f"Error getting blockchain balances: {e}")
            return {}
    
    def get_transactions(self, wallet_address: str, limit: int = 100) -> List[Dict]:
        """
        Obtiene transacciones on-chain (requiere etherscan o similar).
        Nota: Esta implementación es básica. Para producción, usar Etherscan API.
        
        Args:
            wallet_address: Dirección de wallet
            limit: Límite de registros
            
        Returns:
            Lista de transacciones
        """
        try:
            # Esta es una implementación básica
            # En producción, usar: https://etherscan.io/apis
            transactions = []
            
            logger.warning("get_transactions() requires Etherscan API integration")
            return transactions
        
        except Exception as e:
            logger.error(f"Error getting blockchain transactions: {e}")
            return []
    
    def get_prices(self, assets: List[str]) -> Dict[str, Decimal]:
        """
        No implementado (usar PriceFetcher en su lugar).
        
        Args:
            assets: Lista de símbolos
            
        Returns:
            Dict símbolo -> precio
        """
        logger.warning("Prices should be fetched via PriceFetcher, not BlockchainConnector")
        return {}
    
    def get_token_decimals(self, token_address: str) -> int:
        """
        Obtiene decimales de un token ERC-20.
        
        Args:
            token_address: Dirección del contrato
            
        Returns:
            Número de decimales
        """
        try:
            contract = self.w3.eth.contract(
                address=token_address,
                abi=ERC20_ABI
            )
            return contract.functions.decimals().call()
        except Exception as e:
            logger.error(f"Error getting token decimals: {e}")
            return 18  # Default
    
    def get_token_symbol(self, token_address: str) -> str:
        """
        Obtiene símbolo de un token ERC-20.
        
        Args:
            token_address: Dirección del contrato
            
        Returns:
            Símbolo del token
        """
        try:
            contract = self.w3.eth.contract(
                address=token_address,
                abi=ERC20_ABI
            )
            return contract.functions.symbol().call()
        except Exception as e:
            logger.error(f"Error getting token symbol: {e}")
            return "UNKNOWN"


__all__ = ["BlockchainConnector"]
