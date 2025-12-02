"""
Report Generator - Crypto Portfolio Tracker v3
===========================================================================

Servicio para generar reportes del portfolio.

Tipos de reportes:
- Resumen portfolio
- Análisis de performance
- Impuestos (FIFO, LIFO, Average Cost)
- Posiciones DeFi
- Riesgos y alertas

Formatos:
- JSON
- CSV
- PDF (opcional)

Author: Crypto Portfolio Tracker Team
Version: 3.0.0
License: MIT
"""

import logging
import json
import csv
from typing import Dict, List, Optional, Any
from decimal import Decimal
from datetime import datetime
from io import StringIO

from src.database import DatabaseManager
from src.utils import Converters, DateUtils


logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generador centralizado de reportes."""
    
    def __init__(self, db: DatabaseManager):
        """
        Inicializa ReportGenerator.
        
        Args:
            db: Instancia de DatabaseManager
        """
        self.db = db
        logger.info("ReportGenerator initialized")
    
    def generate_portfolio_summary(self, wallet_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Genera resumen del portfolio.
        
        Args:
            wallet_id: ID de wallet (opcional)
            
        Returns:
            Dict con resumen
        """
        try:
            # Obtener wallets
            if wallet_id:
                query = "SELECT * FROM wallets WHERE id = ?"
                wallet_results = self.db.execute_query(query, (wallet_id,))
            else:
                query = "SELECT * FROM wallets"
                wallet_results = self.db.execute_query(query)
            
            wallet_summaries = []
            total_portfolio_value = Decimal(0)
            total_tokens = 0
            
            for wallet_row in wallet_results:
                wid = wallet_row[0]
                address = wallet_row[3]
                
                # Obtener saldos
                balance_query = """
                    SELECT 
                        COUNT(DISTINCT token_symbol) as token_count,
                        SUM(CAST(balance_usd AS REAL)) as total_usd
                    FROM balances 
                    WHERE wallet_id = ?
                """
                balance_results = self.db.execute_query(balance_query, (wid,))
                
                if balance_results:
                    token_count = balance_results[0][0] or 0
                    total_usd = Decimal(balance_results[0][1] or 0)
                    
                    total_portfolio_value += total_usd
                    total_tokens += token_count
                    
                    wallet_summaries.append({
                        'wallet_id': wid,
                        'address': Converters.StringUtils.truncate_address(address),
                        'token_count': token_count,
                        'total_value_usd': float(total_usd),
                    })
            
            return {
                'timestamp': datetime.now().isoformat(),
                'total_portfolio_value_usd': float(total_portfolio_value),
                'total_tokens': total_tokens,
                'total_wallets': len(wallet_summaries),
                'wallets': wallet_summaries,
            }
        
        except Exception as e:
            logger.error(f"Error generating portfolio summary: {e}")
            return {}
    
    def generate_asset_breakdown(self, wallet_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Genera desglose por activo.
        
        Args:
            wallet_id: ID de wallet (opcional)
            
        Returns:
            Dict con desglose
        """
        try:
            if wallet_id:
                query = """
                    SELECT 
                        token_symbol,
                        network,
                        COUNT(*) as wallet_count,
                        SUM(CAST(balance AS REAL)) as total_balance,
                        SUM(CAST(balance_usd AS REAL)) as total_usd
                    FROM balances
                    WHERE wallet_id = ?
                    GROUP BY token_symbol, network
                    ORDER BY total_usd DESC
                """
                results = self.db.execute_query(query, (wallet_id,))
            else:
                query = """
                    SELECT 
                        token_symbol,
                        network,
                        COUNT(*) as wallet_count,
                        SUM(CAST(balance AS REAL)) as total_balance,
                        SUM(CAST(balance_usd AS REAL)) as total_usd
                    FROM balances
                    GROUP BY token_symbol, network
                    ORDER BY total_usd DESC
                """
                results = self.db.execute_query(query)
            
            # Obtener total para calcular porcentajes
            total_query = "SELECT SUM(CAST(balance_usd AS REAL)) FROM balances"
            if wallet_id:
                total_query += " WHERE wallet_id = ?"
                total_result = self.db.execute_query(total_query, (wallet_id,))
            else:
                total_result = self.db.execute_query(total_query)
            
            total_usd = Decimal(total_result[0][0] or 0) if total_result else Decimal(0)
            
            assets = []
            for row in results:
                value = Decimal(row[4] or 0)
                percentage = (value / total_usd * 100) if total_usd > 0 else Decimal(0)
                
                assets.append({
                    'symbol': row[0],
                    'network': row[1],
                    'balance': float(Decimal(row[3] or 0)),
                    'value_usd': float(value),
                    'percentage': float(percentage),
                })
            
            return {
                'timestamp': datetime.now().isoformat(),
                'total_portfolio_usd': float(total_usd),
                'assets': assets,
            }
        
        except Exception as e:
            logger.error(f"Error generating asset breakdown: {e}")
            return {}
    
    def generate_transaction_report(self, wallet_id: int, start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Genera reporte de transacciones.
        
        Args:
            wallet_id: ID de la wallet
            start_date: Fecha inicial (opcional)
            end_date: Fecha final (opcional)
            
        Returns:
            Dict con transacciones
        """
        try:
            query = "SELECT * FROM transactions WHERE wallet_id = ?"
            params = [wallet_id]
            
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)
            
            query += " ORDER BY timestamp DESC"
            
            results = self.db.execute_query(query, tuple(params))
            
            transactions = []
            total_volume = Decimal(0)
            
            for row in results:
                value = Decimal(row[11] or 0)
                total_volume += value
                
                transactions.append({
                    'timestamp': row[13],
                    'type': row[3],
                    'token_in': row[4],
                    'token_out': row[5],
                    'amount_in': float(Decimal(row[6] or 0)),
                    'amount_out': float(Decimal(row[7] or 0)),
                    'fee': float(Decimal(row[8] or 0)),
                    'value_usd': float(value),
                })
            
            return {
                'wallet_id': wallet_id,
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
                'total_transactions': len(transactions),
                'total_volume_usd': float(total_volume),
                'transactions': transactions,
            }
        
        except Exception as e:
            logger.error(f"Error generating transaction report: {e}")
            return {}
    
    def export_to_json(self, data: Dict[str, Any]) -> str:
        """
        Exporta datos a JSON.
        
        Args:
            data: Dict con datos
            
        Returns:
            String JSON
        """
        try:
            return json.dumps(data, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return "{}"
    
    def export_to_csv(self, data: Dict[str, Any], report_type: str = "portfolio") -> str:
        """
        Exporta datos a CSV.
        
        Args:
            data: Dict con datos
            report_type: Tipo de reporte
            
        Returns:
            String CSV
        """
        try:
            output = StringIO()
            
            if report_type == "portfolio":
                writer = csv.DictWriter(output, fieldnames=['wallet_id', 'address', 'token_count', 'total_value_usd'])
                writer.writeheader()
                for wallet in data.get('wallets', []):
                    writer.writerow(wallet)
            
            elif report_type == "assets":
                writer = csv.DictWriter(output, fieldnames=['symbol', 'network', 'balance', 'value_usd', 'percentage'])
                writer.writeheader()
                for asset in data.get('assets', []):
                    writer.writerow(asset)
            
            elif report_type == "transactions":
                writer = csv.DictWriter(output, fieldnames=['timestamp', 'type', 'token_in', 'token_out', 'amount_in', 'amount_out', 'fee', 'value_usd'])
                writer.writeheader()
                for tx in data.get('transactions', []):
                    writer.writerow(tx)
            
            return output.getvalue()
        
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return ""


__all__ = ["ReportGenerator"]
