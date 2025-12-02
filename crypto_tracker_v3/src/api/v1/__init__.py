"""
FastAPI v1 API
==============

Endpoints HTTP para la API pública.

Módulos:
- routes: Endpoints HTTP
- schemas: Pydantic models para validación
- dependencies: Inyección de dependencias
"""

from fastapi import APIRouter

# Crear router
router = APIRouter(prefix="/api/v1", tags=["v1"])

__all__ = ["router"]
