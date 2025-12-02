"""
Pytest Configuration and Fixtures
===========================================================================

Configuración centralizada de pytest.

Incluye:
- Fixtures reutilizables
- Setup/teardown de tests
- Configuración de BD de prueba
- Mock de servicios
- Configuración de logging para tests

Author: Crypto Portfolio Tracker Team
Version: 3.0.0
License: MIT
"""

import pytest
import os
import sys
from pathlib import Path
from typing import Generator

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import DatabaseManager
from src.services import PortfolioService, TaxCalculator, ReportGenerator
from src.utils import ConfigLoader


# ============================================================================
# Database Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def test_db_path() -> Path:
    """Retorna path de BD de prueba."""
    return Path("./test_portfolio.db")


@pytest.fixture(scope="session")
def test_database(test_db_path) -> Generator[DatabaseManager, None, None]:
    """
    Crea BD de prueba para la sesión.
    
    Yields:
        DatabaseManager instance
    """
    # Crear BD
    db = DatabaseManager(
        db_path=str(test_db_path),
        timeout=5,
        echo=False,
    )
    
    # Setup
    db.initialize()
    
    yield db
    
    # Teardown - eliminar BD
    if test_db_path.exists():
        test_db_path.unlink()


@pytest.fixture
def clean_database(test_database) -> DatabaseManager:
    """
    Proporciona BD limpia para cada test.
    
    Limpia todas las tablas antes de cada test.
    """
    # Limpiar tablas
    test_database.clear_all()
    
    yield test_database


# ============================================================================
# Service Fixtures
# ============================================================================

@pytest.fixture
def portfolio_service(clean_database) -> PortfolioService:
    """
    Proporciona PortfolioService con BD limpia.
    
    Returns:
        PortfolioService instance
    """
    return PortfolioService(clean_database)


@pytest.fixture
def tax_calculator(clean_database) -> TaxCalculator:
    """
    Proporciona TaxCalculator con BD limpia.
    
    Returns:
        TaxCalculator instance
    """
    return TaxCalculator(clean_database)


@pytest.fixture
def report_generator(clean_database) -> ReportGenerator:
    """
    Proporciona ReportGenerator con BD limpia.
    
    Returns:
        ReportGenerator instance
    """
    return ReportGenerator(clean_database)


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def config_loader() -> ConfigLoader:
    """
    Proporciona ConfigLoader.
    
    Returns:
        ConfigLoader instance
    """
    return ConfigLoader()


# ============================================================================
# Data Fixtures
# ============================================================================

@pytest.fixture
def sample_wallet_data() -> dict:
    """
    Proporciona datos de sample wallet.
    
    Returns:
        Dict con datos de wallet
    """
    return {
        "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f82e50",
        "wallet_type": "metamask",
        "network": "ethereum",
        "label": "Main Wallet",
    }


@pytest.fixture
def sample_transaction_data() -> dict:
    """
    Proporciona datos de sample transaction.
    
    Returns:
        Dict con datos de transacción
    """
    return {
        "tx_hash": "0x" + "a" * 64,
        "tx_type": "swap",
        "token_in_symbol": "ETH",
        "token_out_symbol": "USDC",
        "amount_in": 1.5,
        "amount_out": 2500.0,
        "fee_paid": 0.001,
        "fee_token": "ETH",
        "network": "ethereum",
    }


@pytest.fixture
def sample_balance_data() -> dict:
    """
    Proporciona datos de sample balance.
    
    Returns:
        Dict con datos de balance
    """
    return {
        "balance": 100.5,
        "balance_usd": 150750.0,
    }


# ============================================================================
# API Client Fixtures
# ============================================================================

@pytest.fixture
def api_client():
    """
    Proporciona cliente HTTP para tests de API.
    
    Returns:
        TestClient instance
    """
    from fastapi.testclient import TestClient
    from main import app
    
    return TestClient(app)


@pytest.fixture
def api_headers() -> dict:
    """
    Proporciona headers por defecto para requests de API.
    
    Returns:
        Dict con headers
    """
    return {
        "X-API-Key": "test-api-key-12345",
        "Content-Type": "application/json",
    }


# ============================================================================
# Pytest Configuration
# ============================================================================

def pytest_configure(config):
    """Configuración inicial de pytest."""
    # Crear marcadores custom
    config.addinivalue_line(
        "markers",
        "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow"
    )


# ============================================================================
# Pytest Hooks
# ============================================================================

def pytest_collection_modifyitems(config, items):
    """Modifica items de tests durante collection."""
    for item in items:
        # Agregar marcadores por defecto
        if "test_" in item.nodeid:
            if "integration" not in item.keywords:
                item.add_marker(pytest.mark.unit)


# ============================================================================
# Logging Configuration
# ============================================================================

@pytest.fixture(autouse=True)
def setup_logging(caplog):
    """
    Configura logging para tests.
    
    Args:
        caplog: Fixture de pytest
    """
    caplog.set_level("DEBUG")
