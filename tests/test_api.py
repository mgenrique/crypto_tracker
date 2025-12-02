"""
Test Suite for API Endpoints
===========================================================================

Tests para los endpoints de FastAPI.

Cubre:
- Health checks
- CRUD de wallets
- Endpoints de portfolio
- Endpoints de transacciones
- Endpoints de tax

Author: Crypto Portfolio Tracker Team
Version: 3.0.0
License: MIT
"""

import pytest

pytestmark = pytest.mark.unit


class TestHealth:
    """Tests para health endpoints."""
    
    def test_health_check(self, api_client):
        """Test health check endpoint."""
        response = api_client.get("/health")
        
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    def test_health_live(self, api_client):
        """Test health/live endpoint."""
        response = api_client.get("/health/live")
        
        assert response.status_code == 200
        assert response.json()["status"] == "alive"
    
    def test_health_ready(self, api_client):
        """Test health/ready endpoint."""
        response = api_client.get("/health/ready")
        
        assert response.status_code == 200
        assert response.json()["status"] == "ready"


class TestRootEndpoints:
    """Tests para endpoints raíz."""
    
    def test_root(self, api_client):
        """Test root endpoint."""
        response = api_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
    
    def test_info(self, api_client):
        """Test info endpoint."""
        response = api_client.get("/info")
        
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data


class TestWalletEndpoints:
    """Tests para endpoints de wallets."""
    
    def test_create_wallet(self, api_client, api_headers, sample_wallet_data):
        """Test crear wallet."""
        response = api_client.post(
            "/api/v1/wallets",
            json=sample_wallet_data,
            headers=api_headers,
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["address"] == sample_wallet_data["address"]
    
    def test_list_wallets(self, api_client, api_headers):
        """Test listar wallets."""
        response = api_client.get(
            "/api/v1/wallets",
            headers=api_headers,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_delete_wallet(self, api_client, api_headers, sample_wallet_data):
        """Test eliminar wallet."""
        # Crear wallet
        create_response = api_client.post(
            "/api/v1/wallets",
            json=sample_wallet_data,
            headers=api_headers,
        )
        wallet_id = create_response.json()["id"]
        
        # Eliminar
        response = api_client.delete(
            f"/api/v1/wallets/{wallet_id}",
            headers=api_headers,
        )
        
        assert response.status_code == 204


class TestPortfolioEndpoints:
    """Tests para endpoints de portfolio."""
    
    def test_get_portfolio_summary(self, api_client, api_headers):
        """Test obtener resumen de portfolio."""
        response = api_client.get(
            "/api/v1/portfolio/summary",
            headers=api_headers,
        )
        
        assert response.status_code in [200, 404]
    
    def test_get_asset_breakdown(self, api_client, api_headers):
        """Test obtener desglose de activos."""
        response = api_client.get(
            "/api/v1/portfolio/assets",
            headers=api_headers,
        )
        
        assert response.status_code in [200, 404]


class TestTransactionEndpoints:
    """Tests para endpoints de transacciones."""
    
    def test_record_transaction(self, api_client, api_headers, sample_wallet_data, sample_transaction_data):
        """Test registrar transacción."""
        # Crear wallet primero
        wallet_response = api_client.post(
            "/api/v1/wallets",
            json=sample_wallet_data,
            headers=api_headers,
        )
        wallet_id = wallet_response.json()["id"]
        
        # Registrar transacción
        response = api_client.post(
            f"/api/v1/wallets/{wallet_id}/transactions",
            json=sample_transaction_data,
            headers=api_headers,
        )
        
        assert response.status_code == 201
    
    def test_get_transactions(self, api_client, api_headers, sample_wallet_data):
        """Test obtener transacciones."""
        # Crear wallet
        wallet_response = api_client.post(
            "/api/v1/wallets",
            json=sample_wallet_data,
            headers=api_headers,
        )
        wallet_id = wallet_response.json()["id"]
        
        # Obtener transacciones
        response = api_client.get(
            f"/api/v1/wallets/{wallet_id}/transactions",
            headers=api_headers,
        )
        
        assert response.status_code in [200, 404]


class TestTaxEndpoints:
    """Tests para endpoints de tax."""
    
    def test_get_tax_report(self, api_client, api_headers, sample_wallet_data):
        """Test obtener reporte de impuestos."""
        # Crear wallet
        wallet_response = api_client.post(
            "/api/v1/wallets",
            json=sample_wallet_data,
            headers=api_headers,
        )
        wallet_id = wallet_response.json()["id"]
        
        # Obtener tax report
        response = api_client.get(
            f"/api/v1/wallets/{wallet_id}/taxes?year=2024&method=FIFO",
            headers=api_headers,
        )
        
        assert response.status_code in [200, 404]


class TestErrorHandling:
    """Tests para manejo de errores."""
    
    def test_missing_api_key(self, api_client):
        """Test missing API key."""
        response = api_client.get("/api/v1/wallets")
        
        assert response.status_code == 401
    
    def test_invalid_wallet_id(self, api_client, api_headers):
        """Test wallet ID inválido."""
        response = api_client.get(
            "/api/v1/wallets/99999",
            headers=api_headers,
        )
        
        assert response.status_code in [404, 422]
    
    def test_invalid_json(self, api_client, api_headers):
        """Test JSON inválido."""
        response = api_client.post(
            "/api/v1/wallets",
            json={"invalid": "data"},
            headers=api_headers,
        )
        
        assert response.status_code == 422
