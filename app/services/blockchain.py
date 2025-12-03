from web3 import Web3
from app.config import settings
from typing import Optional

class BlockchainService:
    def __init__(self):
        self.eth_web3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URI))
        self.arb_web3 = Web3(Web3.HTTPProvider(settings.ARBITRUM_RPC))
        self.poly_web3 = Web3(Web3.HTTPProvider(settings.POLYGON_RPC))
    
    def get_balance(self, address: str, network: str = "ethereum") -> float:
        """Obtener balance en ETH"""
        if not Web3.is_address(address):
            raise ValueError("Invalid address")
        
        web3 = self._get_web3(network)
        balance_wei = web3.eth.get_balance(address)
        balance_eth = Web3.from_wei(balance_wei, 'ether')
        return float(balance_eth)
    
    def _get_web3(self, network: str) -> Web3:
        """Obtener instancia Web3 según red"""
        networks = {
            "ethereum": self.eth_web3,
            "arbitrum": self.arb_web3,
            "polygon": self.poly_web3
        }
        return networks.get(network.lower(), self.eth_web3)
    
    def is_valid_address(self, address: str) -> bool:
        """Validar dirección Ethereum"""
        return Web3.is_address(address)
    
    def get_token_balance(self, address: str, token_contract: str, network: str = "ethereum") -> float:
        """Obtener balance de token ERC20"""
        web3 = self._get_web3(network)
        
        # Simple ABI for ERC20 balanceOf
        abi = [{"constant": True, "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"}]
        
        contract = web3.eth.contract(address=token_contract, abi=abi)
        balance = contract.functions.balanceOf(address).call()
        return balance / 10**18  # Assuming 18 decimals

blockchain_service = BlockchainService()
