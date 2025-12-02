"""
Database Module - Crypto Portfolio Tracker v3
===========================================================================

Módulo de base de datos que incluye:
- Modelos de datos (models.py)
- Gestión de BD (db_manager.py)
- Migraciones (migrations.py)
- Schema SQL (schema.sql)

Uso:
    from src.database.db_manager import DatabaseManager
    from src.database.models import Wallet, Transaction, DefiProtocol
    
    db = DatabaseManager()
    db.initialize_database()
"""

from .db_manager import DatabaseManager
from .models import (
    # Enums
    WalletType,
    TokenType,
    DefiProtocol,
    TransactionType,
    AaveAssetType,
    NetworkType,
    # Dataclasses
    Wallet,
    Token,
    TokenNetwork,
    DeFiPool,
    UniswapV3Position,
    AaveMarket,
    AaveUserPosition,
    Transaction,
    Balance,
    PriceHistory,
    PortfolioSnapshot,
    # Type Aliases
    AddressType,
    TokenAmount,
    PriceUSD,
    HealthFactor,
)
from .migrations import Migration, MigrationManager

__all__ = [
    # Database Manager
    "DatabaseManager",
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
    # Migrations
    "Migration",
    "MigrationManager",
]
