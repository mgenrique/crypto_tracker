"""
Portfolio Service - Crypto Portfolio Tracker v3
===========================================================================

Servicio centralizado para gestionar portfolio.

Responsabilidades:
- Agregar/remover wallets
- Actualizar saldos
- Calcular valor total
- Análisis de composición
- Rendimiento histórico

Author: Crypto Portfolio Tracker Team
Version: 3.0.0
License: MIT
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
from datetime import datetime

from src.database import (
    DatabaseManager,
    Wallet,
    Balance,
    Transaction,
    PortfolioSnapshot,
    WalletType,
    TransactionType,
)
from src.utils import Validators, Converters
from src.utils import ConfigLoader

logger = logging.getLogger(__name__)


class PortfolioService:
    """Servicio centralizado de portfolio."""
    
    def __init__(self, db: DatabaseManager):
        """
        Inicializa PortfolioService.
        
        Args:
            db: Instancia de DatabaseManager
        """
        self.db = db
        self.config = ConfigLoader()
        """
        Ejemplos ver más detalles en .\config\README_config.md
        # Acceder a redes
        ethereum = self.config.get_network("ethereum")
        rpc_url = self.config.get_network_rpc("ethereum")
        
        # Acceder a tokens
        usdc = self.config.get_token("USDC")
        usdc_addr = self.config.get_token_address("USDC", "ethereum")
        
        # Acceder a exchanges
        binance = self.config.get_exchange_config("binance")        
        logger.info("PortfolioService initialized")
        
        """
    
    def add_wallet(self, address: str, wallet_type: str = "metamask", 
                   network: str = "ethereum", label: Optional[str] = None) -> Optional[int]:
        """
        Añade una nueva wallet.
        
        Args:
            address: Dirección blockchain
            wallet_type: Tipo de wallet
            network: Red blockchain
            label: Etiqueta amigable
            
        Returns:
            ID de la wallet o None
        """
        try:
            # Validar dirección
            if not Validators.is_blockchain_address(address, network):
                logger.error(f"Invalid address for {network}: {address}")
                return None
            
            # Validar tipo de wallet
            valid_types = [t.value for t in WalletType]
            if wallet_type not in valid_types:
                logger.error(f"Invalid wallet type: {wallet_type}")
                return None
            
            # Insertar en BD
            query = """
                INSERT INTO wallets (wallet_type, network, address, label)
                VALUES (?, ?, ?, ?)
            """
            wallet_id = self.db.execute_insert(query, (wallet_type, network, address, label))
            
            logger.info(f"Added wallet {address} on {network}")
            return wallet_id
        
        except Exception as e:
            logger.error(f"Error adding wallet: {e}")
            return None
    
    def remove_wallet(self, wallet_id: int) -> bool:
        """
        Elimina una wallet.
        
        Args:
            wallet_id: ID de la wallet
            
        Returns:
            True si exitoso
        """
        try:
            query = "DELETE FROM wallets WHERE id = ?"
            self.db.execute_update(query, (wallet_id,))
            logger.info(f"Removed wallet {wallet_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing wallet: {e}")
            return False
    
    def get_wallets(self) -> List[Dict[str, Any]]:
        """
        Obtiene todas las wallets.
        
        Returns:
            Lista de wallets
        """
        try:
            query = "SELECT * FROM wallets"
            results = self.db.execute_query(query)
            
            wallets = []
            for row in results:
                wallets.append({
                    'id': row[0],
                    'wallet_type': row[1],
                    'network': row[2],
                    'address': row[3],
                    'label': row[4],
                    'created_at': row[5],
                    'updated_at': row[6],
                })
            
            return wallets
        
        except Exception as e:
            logger.error(f"Error getting wallets: {e}")
            return []
    
    def update_balance(self, wallet_id: int, token_symbol: str, 
                      network: str, balance: Decimal, balance_usd: Decimal) -> bool:
        """
        Actualiza saldo de un token.
        
        Args:
            wallet_id: ID de la wallet
            token_symbol: Símbolo del token
            network: Red blockchain
            balance: Cantidad de tokens
            balance_usd: Valor en USD
            
        Returns:
            True si exitoso
        """
        try:
            # Verificar si existe
            check_query = """
                SELECT id FROM balances 
                WHERE wallet_id = ? AND token_symbol = ? AND network = ?
            """
            existing = self.db.execute_query(check_query, (wallet_id, token_symbol, network))
            
            if existing:
                # Actualizar
                update_query = """
                    UPDATE balances 
                    SET balance = ?, balance_usd = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE wallet_id = ? AND token_symbol = ? AND network = ?
                """
                self.db.execute_update(update_query, 
                    (str(balance), str(balance_usd), wallet_id, token_symbol, network))
            else:
                # Insertar
                insert_query = """
                    INSERT INTO balances (wallet_id, token_symbol, network, balance, balance_usd)
                    VALUES (?, ?, ?, ?, ?)
                """
                self.db.execute_insert(insert_query, 
                    (wallet_id, token_symbol, network, str(balance), str(balance_usd)))
            
            return True
        
        except Exception as e:
            logger.error(f"Error updating balance: {e}")
            return False
    
    def get_portfolio_value(self, wallet_id: Optional[int] = None) -> Dict[str, Decimal]:
        """
        Obtiene valor total del portfolio.
        
        Args:
            wallet_id: ID de wallet específica (opcional)
            
        Returns:
            Dict con valores
        """
        try:
            if wallet_id:
                query = "SELECT SUM(CAST(balance_usd AS REAL)) FROM balances WHERE wallet_id = ?"
                results = self.db.execute_query(query, (wallet_id,))
            else:
                query = "SELECT SUM(CAST(balance_usd AS REAL)) FROM balances"
                results = self.db.execute_query(query)
            
            total_usd = Decimal(results[0][0] or 0) if results else Decimal(0)
            
            return {
                'total_usd': total_usd,
                'timestamp': datetime.now(),
            }
        
        except Exception as e:
            logger.error(f"Error getting portfolio value: {e}")
            return {'total_usd': Decimal(0)}
    
    def get_portfolio_composition(self, wallet_id: Optional[int] = None) -> Dict[str, Decimal]:
        """
        Obtiene composición del portfolio.
        
        Args:
            wallet_id: ID de wallet específica (opcional)
            
        Returns:
            Dict símbolo -> porcentaje
        """
        try:
            # Obtener saldos
            if wallet_id:
                query = """
                    SELECT token_symbol, SUM(CAST(balance_usd AS REAL)) as total_usd
                    FROM balances 
                    WHERE wallet_id = ?
                    GROUP BY token_symbol
                    ORDER BY total_usd DESC
                """
                results = self.db.execute_query(query, (wallet_id,))
            else:
                query = """
                    SELECT token_symbol, SUM(CAST(balance_usd AS REAL)) as total_usd
                    FROM balances 
                    GROUP BY token_symbol
                    ORDER BY total_usd DESC
                """
                results = self.db.execute_query(query)
            
            # Obtener total
            total_value = sum(Decimal(row[1] or 0) for row in results)
            
            if total_value == 0:
                return {}
            
            # Calcular porcentajes
            composition = {}
            for symbol, value in results:
                percentage = (Decimal(value or 0) / total_value) * Decimal(100)
                composition[symbol] = percentage
            
            return composition
        
        except Exception as e:
            logger.error(f"Error getting composition: {e}")
            return {}
    
    def record_transaction(self, wallet_id: int, tx_hash: str, 
                          tx_type: str, token_in: str, token_out: str,
                          amount_in: Decimal, amount_out: Decimal,
                          fee: Decimal, fee_token: str, network: str) -> Optional[int]:
        """
        Registra una transacción.
        
        Args:
            wallet_id: ID de la wallet
            tx_hash: Hash de transacción
            tx_type: Tipo (swap, transfer, etc)
            token_in: Token enviado
            token_out: Token recibido
            amount_in: Cantidad enviada
            amount_out: Cantidad recibida
            fee: Fee pagada
            fee_token: Token de fee
            network: Red blockchain
            
        Returns:
            ID de transacción o None
        """
        try:
            query = """
                INSERT INTO transactions 
                (wallet_id, tx_hash, tx_type, token_in_symbol, token_out_symbol, 
                 amount_in, amount_out, fee_paid, fee_token, network, timestamp, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            tx_id = self.db.execute_insert(query, (
                wallet_id, tx_hash, tx_type, token_in, token_out,
                str(amount_in), str(amount_out), str(fee), fee_token,
                network, datetime.now(), 'confirmed'
            ))
            
            logger.info(f"Recorded transaction {tx_hash}")
            return tx_id
        
        except Exception as e:
            logger.error(f"Error recording transaction: {e}")
            return None
    
    def create_snapshot(self, wallet_id: Optional[int] = None) -> bool:
        """
        Crea snapshot del portfolio.
        
        Args:
            wallet_id: ID de wallet (opcional)
            
        Returns:
            True si exitoso
        """
        try:
            portfolio_value = self.get_portfolio_value(wallet_id)
            
            query = """
                INSERT INTO portfolio_snapshots 
                (wallet_id, total_value_usd, total_tokens, data)
                VALUES (?, ?, ?, ?)
            """
            
            # Contar tokens únicos
            if wallet_id:
                count_query = "SELECT COUNT(DISTINCT token_symbol) FROM balances WHERE wallet_id = ?"
                token_count = self.db.execute_query(count_query, (wallet_id,))
            else:
                count_query = "SELECT COUNT(DISTINCT token_symbol) FROM balances"
                token_count = self.db.execute_query(count_query)
            
            num_tokens = token_count[0][0] if token_count else 0
            
            self.db.execute_insert(query, (
                wallet_id,
                str(portfolio_value['total_usd']),
                num_tokens,
                None  # data as JSON (opcional)
            ))
            
            logger.info(f"Created snapshot for wallet {wallet_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error creating snapshot: {e}")
            return False


__all__ = ["PortfolioService"]
