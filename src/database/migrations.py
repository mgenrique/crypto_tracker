"""
Database Migrations - Crypto Portfolio Tracker v3
===========================================================================

Gestión de migraciones de esquema de BD para versiones futuras.

Author: Crypto Portfolio Tracker Team
Version: 3.0.0
License: MIT
"""

import sqlite3
import logging
from typing import List, Callable


logger = logging.getLogger(__name__)


class Migration:
    """Clase base para migraciones."""
    
    version: int = 0
    description: str = ""
    
    @staticmethod
    def up(conn: sqlite3.Connection) -> None:
        """Aplica la migración."""
        raise NotImplementedError
    
    @staticmethod
    def down(conn: sqlite3.Connection) -> None:
        """Revierte la migración."""
        raise NotImplementedError


class MigrationManager:
    """Gestor de migraciones."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.migrations: List[Migration] = []
    
    def register_migration(self, migration: Migration) -> None:
        """Registra una migración."""
        self.migrations.append(migration)
    
    def apply_migrations(self) -> None:
        """Aplica todas las migraciones pendientes."""
        conn = sqlite3.connect(self.db_path)
        try:
            # Crear tabla de control de migraciones si no existe
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_versions (
                    version INTEGER PRIMARY KEY,
                    description TEXT,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            
            # Obtener última versión aplicada
            cursor = conn.cursor()
            cursor.execute("SELECT MAX(version) FROM schema_versions")
            result = cursor.fetchone()
            current_version = result[0] if result[0] else 0
            
            # Aplicar migraciones pendientes
            for migration in self.migrations:
                if migration.version > current_version:
                    logger.info(f"Applying migration {migration.version}: {migration.description}")
                    migration.up(conn)
                    conn.execute(
                        "INSERT INTO schema_versions (version, description) VALUES (?, ?)",
                        (migration.version, migration.description)
                    )
                    conn.commit()
                    logger.info(f"Migration {migration.version} applied successfully")
        
        finally:
            conn.close()


# ============================================================================
# MIGRACIONES FUTURAS (ejemplos)
# ============================================================================

class Migration001AddTokenMetadata(Migration):
    """Migración 001: Agregar metadatos a tokens (Futura)."""
    
    version = 1
    description = "Add token metadata fields"
    
    @staticmethod
    def up(conn: sqlite3.Connection) -> None:
        """Agrega columnas a tokens."""
        conn.execute("""
            ALTER TABLE tokens ADD COLUMN IF NOT EXISTS
            market_cap_rank INTEGER
        """)
        conn.execute("""
            ALTER TABLE tokens ADD COLUMN IF NOT EXISTS
            ath_usd TEXT DEFAULT '0'
        """)
        conn.commit()
    
    @staticmethod
    def down(conn: sqlite3.Connection) -> None:
        """Revierte cambios (crear tabla nueva sin las columnas)."""
        # En SQLite no se pueden borrar columnas fácilmente
        logger.warning("Down migration not supported for this migration")


class Migration002AddLiquidationTracking(Migration):
    """Migración 002: Tracking de liquidaciones Aave (Futura)."""
    
    version = 2
    description = "Add liquidation tracking table"
    
    @staticmethod
    def up(conn: sqlite3.Connection) -> None:
        """Crea tabla para tracking de liquidaciones."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS aave_liquidations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                wallet_id INTEGER NOT NULL,
                liquidator_address TEXT,
                collateral_asset TEXT,
                collateral_amount TEXT,
                debt_asset TEXT,
                debt_amount TEXT,
                discount_percent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(wallet_id) REFERENCES wallets(id)
            )
        """)
        conn.commit()
    
    @staticmethod
    def down(conn: sqlite3.Connection) -> None:
        """Revierte creación de tabla."""
        conn.execute("DROP TABLE IF EXISTS aave_liquidations")
        conn.commit()


__all__ = [
    "Migration",
    "MigrationManager",
    "Migration001AddTokenMetadata",
    "Migration002AddLiquidationTracking",
]
