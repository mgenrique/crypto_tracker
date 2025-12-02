"""
Routes - Crypto Portfolio Tracker v3
===========================================================================

Rutas/Endpoints de FastAPI.

Incluye:
- Health check
- Wallets CRUD
- Balances management
- Transactions
- Portfolio analysis
- Tax calculations
- Reports generation

Author: Crypto Portfolio Tracker Team
Version: 3.0.0
License: MIT
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from datetime import datetime
from decimal import Decimal

from .schemas import (
    WalletCreate, WalletResponse, WalletUpdate, WalletQuery,
    BalanceUpdate, BalanceResponse,
    TransactionCreate, TransactionResponse, TransactionQuery,
    PortfolioSummary, AssetBreakdownReport, TransactionReportResponse,
    TaxReportResponse, HealthCheck, ErrorResponse, CostBasisEnum,
)
from .dependencies import (
    get_portfolio_service, get_tax_calculator, get_report_generator,
    validate_api_key, validate_wallet_id, validate_address, validate_token_symbol,
    get_pagination_params, get_date_range,
)
from src.services import PortfolioService, TaxCalculator, ReportGenerator


logger = logging.getLogger(__name__)


# ============================================================================
# Router Setup
# ============================================================================

router = APIRouter(
    prefix="/api/v1",
    tags=["crypto-portfolio"],
    responses={404: {"description": "Not found"}},
)


# ============================================================================
# Health Check
# ============================================================================

@router.get("/health", response_model=HealthCheck)
async def health_check():
    """
    Health check del servicio.
    
    Returns:
        HealthCheck response
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(),
        "database": "connected",
        "version": "3.0.0",
    }


# ============================================================================
# Wallets Endpoints
# ============================================================================

@router.post("/wallets", response_model=WalletResponse, status_code=status.HTTP_201_CREATED)
async def create_wallet(
    wallet: WalletCreate,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
    api_key: str = Depends(validate_api_key),
):
    """
    Crea una nueva wallet.
    
    Args:
        wallet: Wallet a crear
        portfolio_service: PortfolioService
        api_key: API key validada
        
    Returns:
        WalletResponse
        
    Raises:
        HTTPException si falla
    """
    try:
        # Validar dirección
        await validate_address(wallet.address, wallet.network.value)
        
        # Crear wallet
        wallet_id = portfolio_service.add_wallet(
            address=wallet.address,
            wallet_type=wallet.wallet_type.value,
            network=wallet.network.value,
            label=wallet.label,
        )
        
        if not wallet_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create wallet"
            )
        
        return {
            "id": wallet_id,
            **wallet.dict(),
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating wallet: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/wallets", response_model=List[WalletResponse])
async def list_wallets(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
    api_key: str = Depends(validate_api_key),
):
    """
    Lista todas las wallets.
    
    Args:
        limit: Límite de resultados
        offset: Offset
        portfolio_service: PortfolioService
        api_key: API key validada
        
    Returns:
        Lista de WalletResponse
    """
    try:
        wallets = portfolio_service.get_wallets()
        return wallets[offset:offset + limit]
    
    except Exception as e:
        logger.error(f"Error listing wallets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/wallets/{wallet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_wallet(
    wallet_id: int = Depends(validate_wallet_id),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
    api_key: str = Depends(validate_api_key),
):
    """
    Elimina una wallet.
    
    Args:
        wallet_id: ID de wallet
        portfolio_service: PortfolioService
        api_key: API key validada
        
    Raises:
        HTTPException si falla
    """
    try:
        success = portfolio_service.remove_wallet(wallet_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Wallet not found"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting wallet: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# ============================================================================
# Balance Endpoints
# ============================================================================

@router.put("/wallets/{wallet_id}/balances/{token_symbol}", response_model=BalanceResponse)
async def update_balance(
    wallet_id: int = Depends(validate_wallet_id),
    token_symbol: str = Depends(validate_token_symbol),
    balance_update: BalanceUpdate = None,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
    api_key: str = Depends(validate_api_key),
):
    """
    Actualiza balance de un token.
    
    Args:
        wallet_id: ID de wallet
        token_symbol: Símbolo del token
        balance_update: Datos de actualización
        portfolio_service: PortfolioService
        api_key: API key validada
        
    Returns:
        BalanceResponse
        
    Raises:
        HTTPException si falla
    """
    try:
        success = portfolio_service.update_balance(
            wallet_id=wallet_id,
            token_symbol=token_symbol,
            network="ethereum",  # Parámetro hardcoded por simplicidad
            balance=balance_update.balance,
            balance_usd=balance_update.balance_usd,
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to update balance"
            )
        
        return {
            "wallet_id": wallet_id,
            "token_symbol": token_symbol,
            "network": "ethereum",
            "balance": balance_update.balance,
            "balance_usd": balance_update.balance_usd,
            "last_updated": datetime.now(),
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating balance: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# ============================================================================
# Portfolio Endpoints
# ============================================================================

@router.get("/portfolio/summary", response_model=PortfolioSummary)
async def get_portfolio_summary(
    wallet_id: Optional[int] = None,
    report_generator: ReportGenerator = Depends(get_report_generator),
    api_key: str = Depends(validate_api_key),
):
    """
    Obtiene resumen del portfolio.
    
    Args:
        wallet_id: ID de wallet (opcional)
        report_generator: ReportGenerator
        api_key: API key validada
        
    Returns:
        PortfolioSummary
    """
    try:
        summary = report_generator.generate_portfolio_summary(wallet_id)
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Portfolio not found"
            )
        
        return summary
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting portfolio summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/portfolio/assets", response_model=AssetBreakdownReport)
async def get_asset_breakdown(
    wallet_id: Optional[int] = None,
    report_generator: ReportGenerator = Depends(get_report_generator),
    api_key: str = Depends(validate_api_key),
):
    """
    Obtiene desglose de activos.
    
    Args:
        wallet_id: ID de wallet (opcional)
        report_generator: ReportGenerator
        api_key: API key validada
        
    Returns:
        AssetBreakdownReport
    """
    try:
        breakdown = report_generator.generate_asset_breakdown(wallet_id)
        
        if not breakdown:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset breakdown not found"
            )
        
        return breakdown
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting asset breakdown: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# ============================================================================
# Transactions Endpoints
# ============================================================================

@router.post("/wallets/{wallet_id}/transactions", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def record_transaction(
    wallet_id: int = Depends(validate_wallet_id),
    transaction: TransactionCreate = None,
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
    api_key: str = Depends(validate_api_key),
):
    """
    Registra una transacción.
    
    Args:
        wallet_id: ID de wallet
        transaction: Datos de transacción
        portfolio_service: PortfolioService
        api_key: API key validada
        
    Returns:
        TransactionResponse
        
    Raises:
        HTTPException si falla
    """
    try:
        tx_id = portfolio_service.record_transaction(
            wallet_id=wallet_id,
            tx_hash=transaction.tx_hash,
            tx_type=transaction.tx_type.value,
            token_in=transaction.token_in_symbol,
            token_out=transaction.token_out_symbol,
            amount_in=transaction.amount_in or Decimal(0),
            amount_out=transaction.amount_out or Decimal(0),
            fee=transaction.fee_paid or Decimal(0),
            fee_token=transaction.fee_token,
            network=transaction.network.value,
        )
        
        if not tx_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to record transaction"
            )
        
        return {
            "id": tx_id,
            "wallet_id": wallet_id,
            **transaction.dict(),
            "value_usd": Decimal(0),  # Calculated elsewhere
            "timestamp": datetime.now(),
            "status": "confirmed",
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recording transaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.get("/wallets/{wallet_id}/transactions", response_model=TransactionReportResponse)
async def get_transactions(
    wallet_id: int = Depends(validate_wallet_id),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    report_generator: ReportGenerator = Depends(get_report_generator),
    api_key: str = Depends(validate_api_key),
):
    """
    Obtiene transacciones de una wallet.
    
    Args:
        wallet_id: ID de wallet
        start_date: Fecha inicial (ISO format)
        end_date: Fecha final (ISO format)
        limit: Límite de resultados
        offset: Offset
        report_generator: ReportGenerator
        api_key: API key validada
        
    Returns:
        TransactionReportResponse
    """
    try:
        start, end = await get_date_range(start_date, end_date)
        
        report = report_generator.generate_transaction_report(
            wallet_id=wallet_id,
            start_date=start,
            end_date=end,
        )
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transactions not found"
            )
        
        return report
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting transactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# ============================================================================
# Tax Endpoints
# ============================================================================

@router.get("/wallets/{wallet_id}/taxes", response_model=TaxReportResponse)
async def get_tax_report(
    wallet_id: int = Depends(validate_wallet_id),
    year: int = Query(2024),
    method: CostBasisEnum = Query(CostBasisEnum.FIFO),
    tax_calculator: TaxCalculator = Depends(get_tax_calculator),
    api_key: str = Depends(validate_api_key),
):
    """
    Obtiene reporte de impuestos.
    
    Args:
        wallet_id: ID de wallet
        year: Año fiscal
        method: Método de cost basis
        tax_calculator: TaxCalculator
        api_key: API key validada
        
    Returns:
        TaxReportResponse
        
    Raises:
        HTTPException si falla
    """
    try:
        summary = tax_calculator.get_annual_summary(wallet_id, year)
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tax data not found"
            )
        
        return {
            "wallet_id": wallet_id,
            "year": year,
            "cost_basis_method": method,
            "total_gains": Decimal(0),
            "total_losses": Decimal(0),
            "net_taxable_income": Decimal(0),
            "tokens_summary": summary,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tax report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


__all__ = ["router"]
