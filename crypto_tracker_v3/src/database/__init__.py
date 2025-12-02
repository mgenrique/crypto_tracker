"""
Database Layer
==============

SQLAlchemy ORM y gestión de base de datos.

Módulos:
- manager: DatabaseManager
- models: Modelos ORM
- migrations: Migraciones Alembic
"""

from .manager import DatabaseManager

__all__ = ["DatabaseManager"]
