"""
Services Module - Crypto Portfolio Tracker v3
===========================================================================

Módulo de servicios que incluye:
- PortfolioService (gestión de wallets y saldos)
- TaxCalculator (cálculos de impuestos: FIFO, LIFO, Average)
- ReportGenerator (generación de reportes: JSON, CSV)

Uso:
    from src.services import PortfolioService, TaxCalculator, ReportGenerator
    from src.database import DatabaseManager
    
    # Inicializar BD
    db = DatabaseManager("crypto_tracker.db")
    
    # Servicios
    portfolio = PortfolioService(db)
    taxes = TaxCalculator(db)
    reports = ReportGenerator(db)
    
    # Agregar wallet
    wallet_id = portfolio.add_wallet("0x123...", "ethereum")
    
    # Calcular impuestos con FIFO
    from src.services import CostBasisMethod
    taxes_fifo = TaxCalculator(db, CostBasisMethod.FIFO)
    gains = taxes_fifo.calculate_fifo_gain_loss(wallet_id, "ETH")
    
    # Generar reporte
    summary = reports.generate_portfolio_summary()
    json_report = reports.export_to_json(summary)
"""

from .portfolio_service import PortfolioService
from .tax_calculator import TaxCalculator, CostBasisMethod
from .report_generator import ReportGenerator

__all__ = [
    # Portfolio
    "PortfolioService",
    # Tax
    "TaxCalculator",
    "CostBasisMethod",
    # Reports
    "ReportGenerator",
]
