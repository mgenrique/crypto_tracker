"""
Schemas - Crypto Portfolio Tracker v3
===========================================================================

Esquemas Pydantic para validación de requests y responses.

Incluye:
- Wallets schemas
- Balances schemas
- Transactions schemas
- Reports schemas
- Tax calculations schemas

Author: Crypto Portfolio Tracker Team
Version: 3.0.0
License: MIT
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class WalletTypeEnum(str, Enum):
    """Tipos de wallets soportados."""
    METAMASK = "metamask"
    COINBASE = "coinbase"
    LEDGER = "ledger"
    TREZOR = "trezor"
    MULTISIG = "multisig"
    HARDWARE = "hardware"
    EXCHANGE = "exchange"


class NetworkEnum(str, Enum):
    """Redes blockchain soportadas."""
    ETHEREUM = "ethereum"
    ARBITRUM = "arbitrum"
    BASE = "base"
    POLYGON = "polygon"
    OPTIMISM = "optimism"
    AVALANCHE = "avalanche"
    BITCOIN = "bitcoin"


class TransactionTypeEnum(str, Enum):
    """Tipos de transacciones."""
    SWAP = "swap"
    TRANSFER = "transfer"
    STAKE = "stake"
    UNSTAKE = "unstake"
    CLAIM = "claim"
    MINT = "mint"
    BURN = "burn"
    BRIDGE = "bridge"
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"


class CostBasisEnum(str, Enum):
    """Métodos de cost basis para impuestos."""
    FIFO = "fifo"
    LIFO = "lifo"
    AVERAGE_COST = "average"


# ============================================================================
# Wallet Schemas
# ============================================================================

class WalletBase(BaseModel):
    """Base wallet schema."""
    address: str = Field(..., min_length=26, max_length=66, description="Dirección blockchain")
    wallet_type: WalletTypeEnum = Field(default=WalletTypeEnum.METAMASK)
    network: NetworkEnum = Field(default=NetworkEnum.ETHEREUM)
    label: Optional[str] = Field(None, max_length=50, description="Etiqueta amigable")
    
    @validator('address')
    def validate_address(cls, v):
        """Valida formato de dirección."""
        if not v or len(v) < 26:
            raise ValueError('Dirección inválida')
        return v


class WalletCreate(WalletBase):
    """Request para crear wallet."""
    pass


class WalletUpdate(BaseModel):
    """Request para actualizar wallet."""
    label: Optional[str] = Field(None, max_length=50)
    wallet_type: Optional[WalletTypeEnum] = None


class WalletResponse(WalletBase):
    """Response de wallet."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Balance Schemas
# ============================================================================

class BalanceBase(BaseModel):
    """Base balance schema."""
    token_symbol: str = Field(..., max_length=20, description="Símbolo del token")
    balance: Decimal = Field(..., ge=0, description="Cantidad de tokens")
    balance_usd: Decimal = Field(..., ge=0, description="Valor en USD")
    network: NetworkEnum = Field(default=NetworkEnum.ETHEREUM)


class BalanceUpdate(BaseModel):
    """Request para actualizar balance."""
    balance: Decimal = Field(..., ge=0)
    balance_usd: Decimal = Field(..., ge=0)


class BalanceResponse(BalanceBase):
    """Response de balance."""
    wallet_id: int
    last_updated: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Transaction Schemas
# ============================================================================

class TransactionBase(BaseModel):
    """Base transaction schema."""
    tx_hash: str = Field(..., description="Hash de transacción")
    tx_type: TransactionTypeEnum
    token_in_symbol: Optional[str] = Field(None, max_length=20)
    token_out_symbol: Optional[str] = Field(None, max_length=20)
    amount_in: Optional[Decimal] = Field(None, ge=0)
    amount_out: Optional[Decimal] = Field(None, ge=0)
    fee_paid: Optional[Decimal] = Field(None, ge=0)
    fee_token: Optional[str] = Field(None, max_length=20)
    network: NetworkEnum = Field(default=NetworkEnum.ETHEREUM)


class TransactionCreate(TransactionBase):
    """Request para crear transacción."""
    pass


class TransactionResponse(TransactionBase):
    """Response de transacción."""
    id: int
    wallet_id: int
    value_usd: Decimal
    timestamp: datetime
    status: str
    
    class Config:
        from_attributes = True


# ============================================================================
# Portfolio Schemas
# ============================================================================

class PortfolioComposition(BaseModel):
    """Composición del portfolio."""
    symbol: str
    percentage: Decimal = Field(..., ge=0, le=100)
    value_usd: Decimal


class PortfolioValue(BaseModel):
    """Valor del portfolio."""
    total_usd: Decimal = Field(..., ge=0)
    total_tokens: int
    timestamp: datetime


class PortfolioSummary(BaseModel):
    """Resumen del portfolio."""
    total_portfolio_value_usd: Decimal
    total_tokens: int
    total_wallets: int
    composition: List[PortfolioComposition]
    timestamp: datetime


# ============================================================================
# Asset Breakdown Schemas
# ============================================================================

class AssetBreakdown(BaseModel):
    """Desglose por activo."""
    symbol: str
    network: NetworkEnum
    balance: Decimal
    value_usd: Decimal
    percentage: Decimal = Field(..., ge=0, le=100)


class AssetBreakdownReport(BaseModel):
    """Reporte de desglose de activos."""
    total_portfolio_usd: Decimal
    assets: List[AssetBreakdown]
    timestamp: datetime


# ============================================================================
# Transaction Report Schemas
# ============================================================================

class TransactionSummary(BaseModel):
    """Resumen de transacción para reportes."""
    timestamp: datetime
    type: TransactionTypeEnum
    token_in: Optional[str]
    token_out: Optional[str]
    amount_in: Optional[Decimal]
    amount_out: Optional[Decimal]
    fee: Decimal
    value_usd: Decimal


class TransactionReportResponse(BaseModel):
    """Reporte de transacciones."""
    wallet_id: int
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    total_transactions: int
    total_volume_usd: Decimal
    transactions: List[TransactionSummary]


# ============================================================================
# Tax Calculation Schemas
# ============================================================================

class TaxGainLoss(BaseModel):
    """Ganancias/pérdidas de impuestos."""
    token_symbol: str
    realized_gains: Decimal
    realized_losses: Decimal
    net_gain_loss: Decimal
    method: CostBasisEnum
    timestamp: datetime


class TaxReportResponse(BaseModel):
    """Reporte de impuestos."""
    wallet_id: int
    year: int
    cost_basis_method: CostBasisEnum
    total_gains: Decimal
    total_losses: Decimal
    net_taxable_income: Decimal
    tokens_summary: Dict[str, Dict[str, Decimal]]


# ============================================================================
# Query Schemas
# ============================================================================

class WalletQuery(BaseModel):
    """Query parameters para wallets."""
    network: Optional[NetworkEnum] = None
    wallet_type: Optional[WalletTypeEnum] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class TransactionQuery(BaseModel):
    """Query parameters para transacciones."""
    tx_type: Optional[TransactionTypeEnum] = None
    token_symbol: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


# ============================================================================
# Error Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """Response de error."""
    error: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
    details: Optional[Dict[str, Any]] = None


class ValidationError(BaseModel):
    """Error de validación."""
    field: str
    message: str
    value: Optional[Any] = None


# ============================================================================
# Health Check Schemas
# ============================================================================

class HealthCheck(BaseModel):
    """Health check response."""
    status: str  # "ok" o "error"
    timestamp: datetime
    database: str  # "connected" o "disconnected"
    version: str


__all__ = [
    # Enums
    "WalletTypeEnum",
    "NetworkEnum",
    "TransactionTypeEnum",
    "CostBasisEnum",
    # Wallet
    "WalletCreate",
    "WalletUpdate",
    "WalletResponse",
    # Balance
    "BalanceUpdate",
    "BalanceResponse",
    # Transaction
    "TransactionCreate",
    "TransactionResponse",
    # Portfolio
    "PortfolioComposition",
    "PortfolioValue",
    "PortfolioSummary",
    # Asset
    "AssetBreakdown",
    "AssetBreakdownReport",
    # Reports
    "TransactionReportResponse",
    # Tax
    "TaxGainLoss",
    "TaxReportResponse",
    # Queries
    "WalletQuery",
    "TransactionQuery",
    # Errors
    "ErrorResponse",
    "ValidationError",
    # Health
    "HealthCheck",
]
