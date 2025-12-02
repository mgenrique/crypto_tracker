"""
Data Models - Crypto Portfolio Tracker v3
===========================================================================

Define todos los enums, dataclasses y modelos de datos del proyecto.
Incluye soporte completo para DeFi (Uniswap V2/V3, Aave V2/V3).

Estructura:
    - Enums: Tipos de datos categóricos
    - Dataclasses: Modelos de datos estructurados
    - Type Aliases: Aliases para tipos complejos

Author: Crypto Portfolio Tracker Team
Version: 3.0.0
License: MIT
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import uuid4


# ============================================================================
# ENUMS - Tipos categóricos
# ============================================================================

class WalletType(Enum):
    """Tipos de wallet soportados."""
    METAMASK = "metamask"           # MetaMask browser extension
    PHANTOM = "phantom"             # Phantom wallet (Solana)
    LEDGER = "ledger"               # Ledger hardware wallet
    HARDWARE = "hardware"           # Otros hardware wallets
    SOFTWARE = "software"           # Software wallets genéricos
    EXCHANGE = "exchange"           # Wallets de exchange (Binance, etc)


class TokenType(Enum):
    """Tipos de tokens soportados."""
    NATIVE = "native"               # Token nativo (ETH, SOL, etc)
    ERC20 = "erc20"                 # Estándar ERC-20 (Ethereum)
    SPL = "spl"                     # Estándar SPL (Solana)
    BRIDGED = "bridged"             # Tokens bridged (USDC.e, USDT.e)
    STABLECOIN = "stablecoin"       # Stablecoins
    LP = "lp"                       # LP tokens Uniswap V2
    LP_V3 = "lp_v3"                 # LP NFT positions Uniswap V3
    ATOKEN = "atoken"               # aToken de Aave (aUSDC, aDAI, etc)
    DEBT_TOKEN = "debt_token"       # Debt tokens de Aave
    UNKNOWN = "unknown"             # Token desconocido


class DefiProtocol(Enum):
    """Protocolos DeFi soportados."""
    UNISWAP_V2 = "uniswap_v2"       # Uniswap V2 - Liquidez uniforme
    UNISWAP_V3 = "uniswap_v3"       # Uniswap V3 - Liquidez concentrada
    AAVE_V2 = "aave_v2"             # Aave V2 - Préstamos básicos
    AAVE_V3 = "aave_v3"             # Aave V3 - E-mode, isolation
    CURVE = "curve"                 # Curve Finance
    BALANCER = "balancer"           # Balancer Protocol
    SUSHISWAP = "sushiswap"         # SushiSwap


class TransactionType(Enum):
    """Tipos de transacciones soportadas."""
    # Básicas
    SWAP = "swap"                   # Intercambio de tokens
    TRANSFER = "transfer"           # Transferencia de tokens
    DEPOSIT = "deposit"             # Depósito (general)
    WITHDRAWAL = "withdrawal"       # Retiro (general)
    BRIDGE = "bridge"               # Bridge entre chains
    STAKE = "stake"                 # Staking
    UNSTAKE = "unstake"             # Unstaking
    
    # DeFi - Uniswap V2
    LP_ADD = "liquidity_add"        # Agregar liquidez V2
    LP_REMOVE = "liquidity_remove"  # Remover liquidez V2
    
    # DeFi - Uniswap V3
    LP_V3_MINT = "lp_v3_mint"       # Crear posición NFT V3
    LP_V3_BURN = "lp_v3_burn"       # Quemar posición NFT V3
    LP_V3_COLLECT_FEES = "lp_v3_collect_fees"  # Cobrar fees V3
    LP_V3_INCREASE_LIQUIDITY = "lp_v3_increase_liquidity"  # Aumentar liquidez
    LP_V3_DECREASE_LIQUIDITY = "lp_v3_decrease_liquidity"  # Disminuir liquidez
    
    # DeFi - Aave V2/V3
    AAVE_DEPOSIT = "aave_deposit"                       # Depositar en Aave
    AAVE_WITHDRAW = "aave_withdraw"                     # Retirar de Aave
    AAVE_BORROW = "aave_borrow"                         # Pedir prestado
    AAVE_REPAY = "aave_repay"                           # Pagar préstamo
    AAVE_ENABLE_COLLATERAL = "aave_enable_collateral"   # Habilitar colateral
    AAVE_DISABLE_COLLATERAL = "aave_disable_collateral" # Deshabilitar colateral
    AAVE_LIQUIDATION = "aave_liquidation"               # Liquidación
    AAVE_SWAP_BORROW_MODE = "aave_swap_borrow_mode"     # Cambiar modo deuda


class AaveAssetType(Enum):
    """Tipos de activos en Aave."""
    SUPPLIED = "supplied"               # Activo suministrado (aToken)
    BORROWED_VARIABLE = "borrowed_variable"  # Deuda variable
    BORROWED_STABLE = "borrowed_stable"      # Deuda estable


class NetworkType(Enum):
    """Redes blockchain soportadas."""
    ETHEREUM = "ethereum"           # Ethereum Mainnet
    ARBITRUM = "arbitrum"           # Arbitrum One
    BASE = "base"                   # Base (Coinbase)
    POLYGON = "polygon"             # Polygon
    OPTIMISM = "optimism"           # Optimism
    AVALANCHE = "avalanche"         # Avalanche
    SOLANA = "solana"               # Solana
    BITCOIN = "bitcoin"             # Bitcoin


# ============================================================================
# DATACLASSES - Modelos de datos
# ============================================================================

@dataclass
class Wallet:
    """Modelo de wallet."""
    id: Optional[int] = None
    wallet_type: WalletType = WalletType.METAMASK
    network: str = "ethereum"
    address: str = ""
    label: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def __hash__(self):
        return hash((self.address, self.network))


@dataclass
class Token:
    """Modelo de token."""
    id: Optional[int] = None
    symbol: str = ""
    name: str = ""
    decimals: int = 18
    token_type: TokenType = TokenType.UNKNOWN
    coingecko_id: Optional[str] = None
    contract_address: Optional[str] = None
    logo_url: Optional[str] = None
    
    def __hash__(self):
        return hash(self.symbol)


@dataclass
class TokenNetwork:
    """Modelo de token en una red específica."""
    id: Optional[int] = None
    token_id: int = 0
    network: str = "ethereum"
    contract_address: str = ""
    decimals: int = 18
    is_wrapped: bool = False
    wrapped_of: Optional[str] = None


@dataclass
class DeFiPool:
    """Modelo de pool DeFi."""
    id: Optional[int] = None
    protocol: DefiProtocol = DefiProtocol.UNISWAP_V2
    pool_address: str = ""
    network: str = "ethereum"
    token0_symbol: str = ""
    token1_symbol: str = ""
    token0_address: str = ""
    token1_address: str = ""
    fee_tier: Optional[int] = None  # En bps (0.01% = 1, 0.3% = 30, 1% = 100)
    lp_token_symbol: Optional[str] = None  # Solo Uniswap V2
    tvl_usd: Decimal = Decimal("0")
    volume_24h_usd: Decimal = Decimal("0")
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __hash__(self):
        return hash((self.pool_address, self.network))


@dataclass
class UniswapV3Position:
    """Modelo de posición NFT en Uniswap V3."""
    id: Optional[int] = None
    token_id: int = 0  # NFT token ID (UNIQUE)
    pool_id: int = 0   # Foreign key a defi_pools
    wallet_id: int = 0  # Foreign key a wallets
    lower_tick: int = 0  # Tick inferior del rango
    upper_tick: int = 0  # Tick superior del rango
    liquidity: Decimal = Decimal("0")  # Liquidez depositada
    token0_balance: Decimal = Decimal("0")
    token1_balance: Decimal = Decimal("0")
    uncollected_fees_token0: Decimal = Decimal("0")
    uncollected_fees_token1: Decimal = Decimal("0")
    in_range: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AaveMarket:
    """Modelo de market en Aave."""
    id: Optional[int] = None
    protocol: DefiProtocol = DefiProtocol.AAVE_V3
    market_address: str = ""  # Dirección del asset en Aave
    network: str = "ethereum"
    asset_symbol: str = ""
    atoken_symbol: str = ""
    atoken_address: str = ""
    debt_token_variable_symbol: str = ""
    debt_token_variable_address: str = ""
    debt_token_stable_symbol: Optional[str] = None
    debt_token_stable_address: Optional[str] = None
    ltv: Decimal = Decimal("0.75")  # Loan-to-Value ratio
    liquidation_threshold: Decimal = Decimal("0.80")
    liquidation_bonus: Decimal = Decimal("0.05")
    borrow_apy: Decimal = Decimal("0")
    deposit_apy: Decimal = Decimal("0")
    total_supplied: Decimal = Decimal("0")
    total_borrowed: Decimal = Decimal("0")
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __hash__(self):
        return hash((self.market_address, self.network))


@dataclass
class AaveUserPosition:
    """Modelo de posición de usuario en Aave."""
    id: Optional[int] = None
    wallet_id: int = 0
    market_id: int = 0
    asset_symbol: str = ""
    supplied_amount: Decimal = Decimal("0")
    supplied_as_collateral: bool = False
    borrowed_variable_amount: Decimal = Decimal("0")
    borrowed_stable_amount: Decimal = Decimal("0")
    unclaimed_rewards: Decimal = Decimal("0")
    health_factor: Decimal = Decimal("0")
    snapshot_date: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Transaction:
    """Modelo de transacción."""
    id: Optional[int] = None
    wallet_id: int = 0
    tx_hash: str = ""
    tx_type: TransactionType = TransactionType.TRANSFER
    token_in_symbol: str = ""
    token_out_symbol: str = ""
    amount_in: Decimal = Decimal("0")
    amount_out: Decimal = Decimal("0")
    fee_paid: Decimal = Decimal("0")
    fee_token: str = ""
    price_per_unit: Decimal = Decimal("0")
    value_usd: Decimal = Decimal("0")
    network: str = "ethereum"
    block_number: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: str = "confirmed"
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Balance:
    """Modelo de saldo actual."""
    id: Optional[int] = None
    wallet_id: int = 0
    token_symbol: str = ""
    network: str = "ethereum"
    balance: Decimal = Decimal("0")
    balance_usd: Decimal = Decimal("0")
    last_updated: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PriceHistory:
    """Modelo de histórico de precios."""
    id: Optional[int] = None
    token_symbol: str = ""
    price_usd: Decimal = Decimal("0")
    market_cap_usd: Decimal = Decimal("0")
    volume_24h_usd: Decimal = Decimal("0")
    change_24h_percent: Decimal = Decimal("0")
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PortfolioSnapshot:
    """Modelo de snapshot de portfolio."""
    id: Optional[int] = None
    wallet_id: int = 0
    total_value_usd: Decimal = Decimal("0")
    total_tokens: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# TYPE ALIASES
# ============================================================================

AddressType = str  # Dirección blockchain
TokenAmount = Decimal  # Cantidad de tokens
PriceUSD = Decimal  # Precio en USD
HealthFactor = Decimal  # Health factor de Aave


__all__ = [
    # Enums
    "WalletType",
    "TokenType",
    "DefiProtocol",
    "TransactionType",
    "AaveAssetType",
    "NetworkType",
    # Dataclasses
    "Wallet",
    "Token",
    "TokenNetwork",
    "DeFiPool",
    "UniswapV3Position",
    "AaveMarket",
    "AaveUserPosition",
    "Transaction",
    "Balance",
    "PriceHistory",
    "PortfolioSnapshot",
    # Type Aliases
    "AddressType",
    "TokenAmount",
    "PriceUSD",
    "HealthFactor",
]
