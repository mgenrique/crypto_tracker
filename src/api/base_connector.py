"""
Base Connector - Crypto Portfolio Tracker v3
===========================================================================

Clase abstracta base para todos los conectores API.
Define la interfaz que deben implementar todos los conectores.

Author: Crypto Portfolio Tracker Team
Version: 3.0.0
License: MIT
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime
from decimal import Decimal


logger = logging.getLogger(__name__)


class BaseConnector(ABC):
    """
    Clase abstracta base para conectores API.
    
    Todo conector debe heredar de esta clase e implementar
    los métodos abstractos.
    """
    
    # Propiedades que cada conector debe definir
    name: str = ""
    version: str = "1.0"
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """
        Inicializa el conector.
        
        Args:
            api_key: API key del servicio
            api_secret: API secret del servicio
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = None
        logger.info(f"Initialized {self.name} connector")
    
    @abstractmethod
    def authenticate(self) -> bool:
        """
        Autentica con el servicio.
        
        Returns:
            True si autenticación exitosa
        """
        pass
    
    @abstractmethod
    def get_account_info(self) -> Dict[str, Any]:
        """
        Obtiene información de la cuenta.
        
        Returns:
            Dict con info de cuenta
        """
        pass
    
    @abstractmethod
    def get_balances(self, asset: Optional[str] = None) -> Dict[str, Decimal]:
        """
        Obtiene saldos.
        
        Args:
            asset: Activo específico (opcional)
            
        Returns:
            Dict símbolo -> saldo
        """
        pass
    
    @abstractmethod
    def get_transactions(self, asset: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """
        Obtiene histórico de transacciones.
        
        Args:
            asset: Activo específico (opcional)
            limit: Límite de registros
            
        Returns:
            Lista de transacciones
        """
        pass
    
    @abstractmethod
    def get_prices(self, assets: List[str]) -> Dict[str, Decimal]:
        """
        Obtiene precios actuales.
        
        Args:
            assets: Lista de símbolos
            
        Returns:
            Dict símbolo -> precio USD
        """
        pass
    
    def close(self) -> None:
        """Cierra sesión y libera recursos."""
        if self.session:
            self.session.close()
        logger.info(f"Closed {self.name} connector")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


__all__ = ["BaseConnector"]
