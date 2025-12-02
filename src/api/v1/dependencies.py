"""
Dependencies - Crypto Portfolio Tracker v3
===========================================================================

Dependencias centralizadas para FastAPI.

Incluye:
- Inyección de BD
- Inyección de servicios
- Validación de headers
- Manejo de errores
- Logging centralizado

Author: Crypto Portfolio Tracker Team
Version: 3.0.0
License: MIT
"""

import logging
from typing import Optional
from fastapi import Depends, HTTPException, Header, status
from functools import lru_cache

from src.database import DatabaseManager
from src.services import PortfolioService, TaxCalculator, ReportGenerator, CostBasisMethod
from src.utils import ConfigLoader, LoggerSetup, Validators


logger = logging.getLogger(__name__)


# ============================================================================
# Configuration & Setup
# ============================================================================

@lru_cache()
def get_config() -> ConfigLoader:
    """
    Obtiene configuración global (cached).
    
    Returns:
        ConfigLoader instance
    """
    return ConfigLoader()


@lru_cache()
def get_database(config: ConfigLoader = Depends(get_config)) -> DatabaseManager:
    """
    Obtiene instancia de BD (cached).
    
    Args:
        config: ConfigLoader
        
    Returns:
        DatabaseManager instance
    """
    db_config = config.get_database_config()
    db = DatabaseManager(
        db_path=db_config['path'],
        timeout=db_config['timeout'],
        echo=db_config['echo']
    )
    return db


# ============================================================================
# Service Dependencies
# ============================================================================

def get_portfolio_service(db: DatabaseManager = Depends(get_database)) -> PortfolioService:
    """
    Obtiene PortfolioService.
    
    Args:
        db: DatabaseManager
        
    Returns:
        PortfolioService instance
    """
    return PortfolioService(db)


def get_tax_calculator(
    db: DatabaseManager = Depends(get_database),
    cost_basis_method: CostBasisMethod = CostBasisMethod.FIFO
) -> TaxCalculator:
    """
    Obtiene TaxCalculator.
    
    Args:
        db: DatabaseManager
        cost_basis_method: Método de cost basis
        
    Returns:
        TaxCalculator instance
    """
    return TaxCalculator(db, cost_basis_method)


def get_report_generator(db: DatabaseManager = Depends(get_database)) -> ReportGenerator:
    """
    Obtiene ReportGenerator.
    
    Args:
        db: DatabaseManager
        
    Returns:
        ReportGenerator instance
    """
    return ReportGenerator(db)


# ============================================================================
# Validation Dependencies
# ============================================================================

async def validate_api_key(x_api_key: Optional[str] = Header(None)) -> str:
    """
    Valida API key.
    
    Args:
        x_api_key: API key en header
        
    Returns:
        API key validada
        
    Raises:
        HTTPException si no válida
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    # En producción, verificar contra base de datos
    if not Validators.validate_api_key(x_api_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return x_api_key


async def validate_wallet_id(wallet_id: int) -> int:
    """
    Valida que wallet_id sea válido.
    
    Args:
        wallet_id: ID de wallet
        
    Returns:
        wallet_id validado
        
    Raises:
        HTTPException si no válido
    """
    if wallet_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid wallet ID"
        )
    
    return wallet_id


async def validate_address(address: str, network: str = "ethereum") -> str:
    """
    Valida dirección blockchain.
    
    Args:
        address: Dirección a validar
        network: Red blockchain
        
    Returns:
        Dirección validada
        
    Raises:
        HTTPException si no válida
    """
    if not Validators.is_blockchain_address(address, network):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {network} address"
        )
    
    return address


async def validate_token_symbol(symbol: str) -> str:
    """
    Valida símbolo de token.
    
    Args:
        symbol: Símbolo del token
        
    Returns:
        Símbolo validado
        
    Raises:
        HTTPException si no válido
    """
    if not Validators.is_token_symbol(symbol):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token symbol"
        )
    
    return symbol.upper()


# ============================================================================
# Query Parameters
# ============================================================================

async def get_pagination_params(
    limit: int = 100,
    offset: int = 0
) -> tuple:
    """
    Obtiene parámetros de paginación.
    
    Args:
        limit: Límite de resultados (max 1000)
        offset: Offset
        
    Returns:
        Tupla (limit, offset)
        
    Raises:
        HTTPException si parámetros inválidos
    """
    if limit < 1 or limit > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Limit must be between 1 and 1000"
        )
    
    if offset < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Offset cannot be negative"
        )
    
    return (limit, offset)


async def get_date_range(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> tuple:
    """
    Obtiene rango de fechas validado.
    
    Args:
        start_date: Fecha inicial (ISO format)
        end_date: Fecha final (ISO format)
        
    Returns:
        Tupla (start_date, end_date)
        
    Raises:
        HTTPException si fechas inválidas
    """
    try:
        from datetime import datetime
        
        start = None
        end = None
        
        if start_date:
            start = datetime.fromisoformat(start_date)
        
        if end_date:
            end = datetime.fromisoformat(end_date)
        
        if start and end and start > end:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date cannot be after end_date"
            )
        
        return (start, end)
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid date format: {e}"
        )


# ============================================================================
# Error Handling
# ============================================================================

async def handle_database_error(error: Exception) -> dict:
    """
    Maneja errores de BD.
    
    Args:
        error: Excepción
        
    Returns:
        Dict con info del error
    """
    logger.error(f"Database error: {error}")
    return {
        "error": "database_error",
        "message": "An error occurred while accessing the database",
    }


async def handle_validation_error(error: Exception) -> dict:
    """
    Maneja errores de validación.
    
    Args:
        error: Excepción
        
    Returns:
        Dict con info del error
    """
    logger.warning(f"Validation error: {error}")
    return {
        "error": "validation_error",
        "message": str(error),
    }


# ============================================================================
# Logging
# ============================================================================

def get_logger(name: str) -> logging.Logger:
    """
    Obtiene logger por nombre.
    
    Args:
        name: Nombre del logger
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


__all__ = [
    # Config
    "get_config",
    "get_database",
    # Services
    "get_portfolio_service",
    "get_tax_calculator",
    "get_report_generator",
    # Validation
    "validate_api_key",
    "validate_wallet_id",
    "validate_address",
    "validate_token_symbol",
    # Query Parameters
    "get_pagination_params",
    "get_date_range",
    # Error Handling
    "handle_database_error",
    "handle_validation_error",
    # Logging
    "get_logger",
]
