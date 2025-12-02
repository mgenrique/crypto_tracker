"""
Portfolio Service
=================

Portfolio management business logic.
Handles wallets, transactions, and balance tracking.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from datetime import datetime
from typing import List, Optional, Dict, Any
import logging

from src.database.models import (
    WalletModel, TransactionModel, BalanceModel
)

logger = logging.getLogger(__name__)


class PortfolioService:
    """Portfolio business logic service"""

    def __init__(self, db_manager):
        """
        Initialize portfolio service
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db_manager = db_manager

    def add_wallet(self, 
                   address: str, 
                   wallet_type: str, 
                   network: str, 
                   label: str) -> Dict[str, Any]:
        """
        Add new wallet to portfolio
        
        Args:
            address: Wallet address (0x... for Ethereum, or any format)
            wallet_type: 'hot', 'cold', 'hardware', 'exchange', 'defi'
            network: 'ethereum', 'arbitrum', 'base', 'polygon', etc
            label: User-friendly name
            
        Returns:
            Created wallet dict
        """
        try:
            with self.db_manager.session_context() as session:
                # Check if wallet already exists
                existing = session.query(WalletModel).filter_by(
                    address=address,
                    network=network
                ).first()
                
                if existing:
                    logger.warning(f"Wallet {address} on {network} already exists")
                    return {
                        "id": existing.id,
                        "address": existing.address,
                        "network": existing.network,
                    
