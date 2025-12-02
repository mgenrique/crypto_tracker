"""
Test Suite for Services
===========================================================================

Tests para PortfolioService, TaxCalculator, ReportGenerator.

Cubre:
- CRUD de wallets
- Gestión de balances
- Cálculo de impuestos
- Generación de reportes

Author: Crypto Portfolio Tracker Team
Version: 3.0.0
License: MIT
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta

pytestmark = pytest.mark.unit


class TestPortfolioService:
    """Tests para PortfolioService."""
    
    def test_add_wallet(self, portfolio_service, sample_wallet_data):
        """Test agregar wallet."""
        wallet_id = portfolio_service.add_wallet(
            address=sample_wallet_data["address"],
            wallet_type=sample_wallet_data["wallet_type"],
            network=sample_wallet_data["network"],
            label=sample_wallet_data["label"],
        )
        
        assert wallet_id is not None
        assert isinstance(wallet_id, int)
        assert wallet_id > 0
    
    def test_get_wallets(self, portfolio_service, sample_wallet_data):
        """Test obtener wallets."""
        # Agregar wallet
        portfolio_service.add_wallet(
            address=sample_wallet_data["address"],
            wallet_type=sample_wallet_data["wallet_type"],
            network=sample_wallet_data["network"],
            label=sample_wallet_data["label"],
        )
        
        # Obtener wallets
        wallets = portfolio_service.get_wallets()
        
        assert wallets is not None
        assert len(wallets) >= 1
    
    def test_remove_wallet(self, portfolio_service, sample_wallet_data):
        """Test eliminar wallet."""
        # Agregar wallet
        wallet_id = portfolio_service.add_wallet(
            address=sample_wallet_data["address"],
            wallet_type=sample_wallet_data["wallet_type"],
            network=sample_wallet_data["network"],
            label=sample_wallet_data["label"],
        )
        
        # Eliminar
        success = portfolio_service.remove_wallet(wallet_id)
        
        assert success is True
    
    def test_update_balance(self, portfolio_service, sample_wallet_data, sample_balance_data):
        """Test actualizar balance."""
        # Agregar wallet
        wallet_id = portfolio_service.add_wallet(
            address=sample_wallet_data["address"],
            wallet_type=sample_wallet_data["wallet_type"],
            network=sample_wallet_data["network"],
            label=sample_wallet_data["label"],
        )
        
        # Actualizar balance
        success = portfolio_service.update_balance(
            wallet_id=wallet_id,
            token_symbol="ETH",
            network="ethereum",
            balance=Decimal(str(sample_balance_data["balance"])),
            balance_usd=Decimal(str(sample_balance_data["balance_usd"])),
        )
        
        assert success is True
    
    def test_record_transaction(self, portfolio_service, sample_wallet_data, sample_transaction_data):
        """Test registrar transacción."""
        # Agregar wallet
        wallet_id = portfolio_service.add_wallet(
            address=sample_wallet_data["address"],
            wallet_type=sample_wallet_data["wallet_type"],
            network=sample_wallet_data["network"],
            label=sample_wallet_data["label"],
        )
        
        # Registrar transacción
        tx_id = portfolio_service.record_transaction(
            wallet_id=wallet_id,
            tx_hash=sample_transaction_data["tx_hash"],
            tx_type=sample_transaction_data["tx_type"],
            token_in=sample_transaction_data["token_in_symbol"],
            token_out=sample_transaction_data["token_out_symbol"],
            amount_in=Decimal(str(sample_transaction_data["amount_in"])),
            amount_out=Decimal(str(sample_transaction_data["amount_out"])),
            fee=Decimal(str(sample_transaction_data["fee_paid"])),
            fee_token=sample_transaction_data["fee_token"],
            network=sample_transaction_data["network"],
        )
        
        assert tx_id is not None
        assert isinstance(tx_id, int)
        assert tx_id > 0


class TestTaxCalculator:
    """Tests para TaxCalculator."""
    
    def test_get_annual_summary(self, tax_calculator):
        """Test obtener resumen anual."""
        summary = tax_calculator.get_annual_summary(wallet_id=1, year=2024)
        
        assert summary is not None
        assert isinstance(summary, dict)
    
    def test_calculate_gains(self, tax_calculator, portfolio_service, sample_wallet_data):
        """Test calcular ganancias."""
        # Agregar wallet
        wallet_id = portfolio_service.add_wallet(
            address=sample_wallet_data["address"],
            wallet_type=sample_wallet_data["wallet_type"],
            network=sample_wallet_data["network"],
            label=sample_wallet_data["label"],
        )
        
        # Calcular ganancias
        gains = tax_calculator.calculate_gains(
            wallet_id=wallet_id,
            year=2024,
        )
        
        assert gains is not None
        assert isinstance(gains, (int, float, Decimal))


class TestReportGenerator:
    """Tests para ReportGenerator."""
    
    def test_generate_portfolio_summary(self, report_generator):
        """Test generar resumen de portfolio."""
        summary = report_generator.generate_portfolio_summary(wallet_id=None)
        
        assert summary is not None
        assert isinstance(summary, dict)
    
    def test_generate_asset_breakdown(self, report_generator):
        """Test generar desglose de activos."""
        breakdown = report_generator.generate_asset_breakdown(wallet_id=None)
        
        assert breakdown is not None
        assert isinstance(breakdown, dict)
    
    def test_generate_transaction_report(self, report_generator):
        """Test generar reporte de transacciones."""
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()
        
        report = report_generator.generate_transaction_report(
            wallet_id=None,
            start_date=start_date,
            end_date=end_date,
        )
        
        assert report is not None
        assert isinstance(report, dict)
