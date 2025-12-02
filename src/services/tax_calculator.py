"""
Tax Calculator - Crypto Portfolio Tracker v3
===========================================================================

Servicio para cálculos de impuestos sobre criptomonedas.

Soporta:
- FIFO (First In First Out)
- LIFO (Last In First Out)
- Average Cost
- Ganancia/Pérdida realizada
- Reportes de impuestos

Nota: Consulta con asesor fiscal local. Este código es educativo.

Author: Crypto Portfolio Tracker Team
Version: 3.0.0
License: MIT
"""

import logging
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from datetime import datetime
from enum import Enum

from src.database import DatabaseManager, Transaction, TransactionType
from src.utils import Converters


logger = logging.getLogger(__name__)


class CostBasisMethod(Enum):
    """Métodos para calcular cost basis."""
    FIFO = "fifo"           # First In First Out
    LIFO = "lifo"           # Last In Last Out
    AVERAGE_COST = "average"  # Costo promedio


class TaxCalculator:
    """Calculador de impuestos para criptomonedas."""
    
    def __init__(self, db: DatabaseManager, cost_basis_method: CostBasisMethod = CostBasisMethod.FIFO):
        """
        Inicializa TaxCalculator.
        
        Args:
            db: Instancia de DatabaseManager
            cost_basis_method: Método para calcular cost basis
        """
        self.db = db
        self.cost_basis_method = cost_basis_method
        logger.info(f"TaxCalculator initialized with {cost_basis_method.value} method")
    
    def get_transaction_history(self, wallet_id: int, token_symbol: str) -> List[Dict]:
        """
        Obtiene histórico de transacciones para un token.
        
        Args:
            wallet_id: ID de la wallet
            token_symbol: Símbolo del token
            
        Returns:
            Lista de transacciones ordenadas por timestamp
        """
        try:
            query = """
                SELECT * FROM transactions 
                WHERE wallet_id = ? AND (token_in_symbol = ? OR token_out_symbol = ?)
                ORDER BY timestamp ASC
            """
            results = self.db.execute_query(query, (wallet_id, token_symbol, token_symbol))
            
            transactions = []
            for row in results:
                transactions.append({
                    'id': row[0],
                    'type': row[3],
                    'token_in': row[4],
                    'token_out': row[5],
                    'amount_in': Decimal(row[6] or 0),
                    'amount_out': Decimal(row[7] or 0),
                    'fee': Decimal(row[8] or 0),
                    'price_per_unit': Decimal(row[10] or 0),
                    'value_usd': Decimal(row[11] or 0),
                    'timestamp': row[13],
                })
            
            return transactions
        
        except Exception as e:
            logger.error(f"Error getting transaction history: {e}")
            return []
    
    def calculate_fifo_gain_loss(self, wallet_id: int, token_symbol: str) -> Dict[str, Decimal]:
        """
        Calcula ganancia/pérdida usando FIFO.
        
        Args:
            wallet_id: ID de la wallet
            token_symbol: Símbolo del token
            
        Returns:
            Dict con ganancias/pérdidas
        """
        try:
            transactions = self.get_transaction_history(wallet_id, token_symbol)
            
            fifo_queue = []  # (cantidad, cost_per_unit, timestamp)
            realized_gains = Decimal(0)
            realized_losses = Decimal(0)
            
            for tx in transactions:
                if tx['token_in'] == token_symbol:
                    # Compra
                    cost_per_unit = tx['value_usd'] / tx['amount_in'] if tx['amount_in'] > 0 else Decimal(0)
                    fifo_queue.append((tx['amount_in'], cost_per_unit, tx['timestamp']))
                
                elif tx['token_out'] == token_symbol:
                    # Venta/salida
                    amount_to_sell = tx['amount_out']
                    sale_price_per_unit = tx['value_usd'] / tx['amount_out'] if tx['amount_out'] > 0 else Decimal(0)
                    
                    while amount_to_sell > 0 and fifo_queue:
                        qty, cost, ts = fifo_queue.pop(0)
                        
                        if qty <= amount_to_sell:
                            # Vender todo este lote
                            gain = (sale_price_per_unit - cost) * qty
                            if gain > 0:
                                realized_gains += gain
                            else:
                                realized_losses += abs(gain)
                            amount_to_sell -= qty
                        else:
                            # Vender parte del lote
                            gain = (sale_price_per_unit - cost) * amount_to_sell
                            if gain > 0:
                                realized_gains += gain
                            else:
                                realized_losses += abs(gain)
                            # Retornar el resto del lote
                            fifo_queue.insert(0, (qty - amount_to_sell, cost, ts))
                            amount_to_sell = Decimal(0)
            
            return {
                'realized_gains': realized_gains,
                'realized_losses': realized_losses,
                'net_gain_loss': realized_gains - realized_losses,
                'method': 'FIFO',
            }
        
        except Exception as e:
            logger.error(f"Error calculating FIFO gain/loss: {e}")
            return {}
    
    def calculate_average_cost_gain_loss(self, wallet_id: int, token_symbol: str) -> Dict[str, Decimal]:
        """
        Calcula ganancia/pérdida usando costo promedio.
        
        Args:
            wallet_id: ID de la wallet
            token_symbol: Símbolo del token
            
        Returns:
            Dict con ganancias/pérdidas
        """
        try:
            transactions = self.get_transaction_history(wallet_id, token_symbol)
            
            total_quantity = Decimal(0)
            total_cost = Decimal(0)
            realized_gains = Decimal(0)
            realized_losses = Decimal(0)
            
            for tx in transactions:
                if tx['token_in'] == token_symbol:
                    # Compra
                    total_cost += tx['value_usd']
                    total_quantity += tx['amount_in']
                
                elif tx['token_out'] == token_symbol:
                    # Venta
                    if total_quantity > 0:
                        average_cost = total_cost / total_quantity
                        sale_price_per_unit = tx['value_usd'] / tx['amount_out'] if tx['amount_out'] > 0 else Decimal(0)
                        
                        gain = (sale_price_per_unit - average_cost) * tx['amount_out']
                        if gain > 0:
                            realized_gains += gain
                        else:
                            realized_losses += abs(gain)
                        
                        # Ajustar totales
                        total_cost = total_cost * (total_quantity - tx['amount_out']) / total_quantity
                        total_quantity -= tx['amount_out']
            
            return {
                'realized_gains': realized_gains,
                'realized_losses': realized_losses,
                'net_gain_loss': realized_gains - realized_losses,
                'method': 'AVERAGE_COST',
                'unrealized_cost': total_cost,
                'unrealized_quantity': total_quantity,
            }
        
        except Exception as e:
            logger.error(f"Error calculating average cost gain/loss: {e}")
            return {}
    
    def get_annual_summary(self, wallet_id: int, year: int) -> Dict[str, Decimal]:
        """
        Obtiene resumen de impuestos del año.
        
        Args:
            wallet_id: ID de la wallet
            year: Año fiscal
            
        Returns:
            Dict con totales del año
        """
        try:
            query = """
                SELECT token_in_symbol, token_out_symbol, 
                       SUM(CAST(value_usd AS REAL)) as total_value
                FROM transactions 
                WHERE wallet_id = ? AND strftime('%Y', timestamp) = ?
                GROUP BY CASE WHEN token_in_symbol IS NOT NULL THEN token_in_symbol ELSE token_out_symbol END
            """
            
            results = self.db.execute_query(query, (wallet_id, str(year)))
            
            summary = {}
            for row in results:
                token = row[0] or row[1]
                summary[token] = Decimal(row[2] or 0)
            
            return summary
        
        except Exception as e:
            logger.error(f"Error getting annual summary: {e}")
            return {}


__all__ = ["TaxCalculator", "CostBasisMethod"]
