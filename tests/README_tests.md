# Tests - Test Suite for Crypto Portfolio Tracker v3

## 📊 Estructura de tests

```
tests/
├── __init__.py
├── conftest.py              ← Configuración y fixtures
├── test_services.py         ← Tests de servicios
├── test_api.py             ← Tests de API endpoints
├── test_utils.py           ← Tests de utilidades (opcional)
└── integration/            ← Tests de integración (opcional)
    └── test_blockchain.py
```

## 🚀 Setup Rápido

### 1. Instalar dependencias de test

```bash
pip install pytest pytest-cov pytest-asyncio fastapi[all] httpx
```

O usando el archivo de requirements:

```bash
pip install -r requirements-test.txt
```

### 2. Ejecutar tests

```bash
# Todos los tests
pytest

# Con verbose
pytest -v

# Solo tests unitarios
pytest -m unit

# Con coverage
pytest --cov=src --cov-report=html

# Tests específicos
pytest tests/test_services.py
pytest tests/test_api.py::TestWalletEndpoints::test_create_wallet
```

## 📋 Archivos en esta carpeta

### 1. `conftest.py` (Configuración)
Fixtures centralizadas para todos los tests.

**Fixtures disponibles:**
- `test_database` - BD de prueba (session scope)
- `clean_database` - BD limpia por test (function scope)
- `portfolio_service` - PortfolioService
- `tax_calculator` - TaxCalculator
- `report_generator` - ReportGenerator
- `api_client` - TestClient para API
- `api_headers` - Headers por defecto para requests
- `sample_wallet_data` - Datos de sample wallet
- `sample_transaction_data` - Datos de sample transaction
- `sample_balance_data` - Datos de sample balance

### 2. `test_services.py` (Service Tests)
Tests para la lógica de negocios.

**Clases:**
- `TestPortfolioService` - Tests de gestión de portafolio
  - test_add_wallet
  - test_get_wallets
  - test_remove_wallet
  - test_update_balance
  - test_record_transaction

- `TestTaxCalculator` - Tests de cálculo de impuestos
  - test_get_annual_summary
  - test_calculate_gains

- `TestReportGenerator` - Tests de generación de reportes
  - test_generate_portfolio_summary
  - test_generate_asset_breakdown
  - test_generate_transaction_report

### 3. `test_api.py` (API Tests)
Tests para los endpoints HTTP.

**Clases:**
- `TestHealth` - Health checks
  - test_health_check
  - test_health_live
  - test_health_ready

- `TestRootEndpoints` - Endpoints raíz
  - test_root
  - test_info

- `TestWalletEndpoints` - Wallets
  - test_create_wallet
  - test_list_wallets
  - test_delete_wallet

- `TestPortfolioEndpoints` - Portfolio
  - test_get_portfolio_summary
  - test_get_asset_breakdown

- `TestTransactionEndpoints` - Transacciones
  - test_record_transaction
  - test_get_transactions

- `TestTaxEndpoints` - Impuestos
  - test_get_tax_report

- `TestErrorHandling` - Manejo de errores
  - test_missing_api_key
  - test_invalid_wallet_id
  - test_invalid_json

### 4. `pytest.ini` (Configuración)
Configuración de pytest.

**Contiene:**
- Rutas de tests
- Markers (unit, integration, slow, e2e)
- Opciones de output
- Configuración de coverage

## 🧪 Uso de Fixtures

### Fixture de BD limpia

```python
def test_add_wallet(self, portfolio_service, sample_wallet_data):
    """Test con BD limpia automáticamente."""
    wallet_id = portfolio_service.add_wallet(
        address=sample_wallet_data["address"],
        wallet_type=sample_wallet_data["wallet_type"],
        network=sample_wallet_data["network"],
        label=sample_wallet_data["label"],
    )
    
    assert wallet_id is not None
```

### Fixture de API client

```python
def test_health_check(self, api_client):
    """Test con cliente HTTP."""
    response = api_client.get("/health")
    
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
```

### Fixture de datos de sample

```python
def test_create_wallet(self, api_client, api_headers, sample_wallet_data):
    """Test usando datos de sample."""
    response = api_client.post(
        "/api/v1/wallets",
        json=sample_wallet_data,
        headers=api_headers,
    )
    
    assert response.status_code == 201
```

## 📊 Coverage

### Generar reporte de coverage

```bash
pytest --cov=src --cov-report=html
```

Abre `htmlcov/index.html` en navegador.

### Mostrar coverage en consola

```bash
pytest --cov=src --cov-report=term-missing
```

### Target de coverage

```bash
# Fallar si coverage < 80%
pytest --cov=src --cov-fail-under=80
```

## 🏷️ Marcadores (Markers)

### Ejecutar por tipo

```bash
# Solo unit tests
pytest -m unit

# Solo integration tests
pytest -m integration

# Excluir slow tests
pytest -m "not slow"

# Unit tests pero no slow
pytest -m "unit and not slow"
```

### Crear custom markers

En `conftest.py`:
```python
@pytest.mark.custom_marker
def test_something():
    pass
```

Usar:
```bash
pytest -m custom_marker
```

## 🔧 Debugging

### Ejecutar con debugging

```bash
# Parar en primer error
pytest -x

# Parar y lanzar debugger en error
pytest --pdb

# Mostrar print statements
pytest -s

# Verbose + print statements
pytest -vs
```

### Inspeccionar valores

```python
def test_something(self):
    result = compute()
    print(f"Result: {result}")  # Visible con pytest -s
    assert result == expected
```

## ⚠️ Errores comunes

### Error: "No module named 'src'"

**Solución:** Asegurar que `sys.path` incluye raíz en conftest.py
```python
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Error: "test_database.db locked"

**Solución:** Asegurar que BD se elimina en teardown
```python
if test_db_path.exists():
    test_db_path.unlink()
```

### Error: "fixture not found"

**Solución:** Verificar que `conftest.py` esté en directorio `tests/`

## 📈 Métricas de tests

```bash
# Contar tests
pytest --collect-only -q

# Listar todos los tests
pytest --collect-only

# Mostrar duración de tests
pytest --durations=10
```

## 🔄 Integración Continua

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: 3.10
      - run: pip install -r requirements-test.txt
      - run: pytest --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## 📚 Recursos

- Pytest docs: https://docs.pytest.org/
- Fixture docs: https://docs.pytest.org/en/stable/fixture.html
- Coverage docs: https://pytest-cov.readthedocs.io/

## 🎯 Próximos pasos

1. Ejecutar tests:
   ```bash
   pytest -v
   ```

2. Verificar coverage:
   ```bash
   pytest --cov=src
   ```

3. Agregar más tests según sea necesario

4. Configurar CI/CD para ejecutar tests automáticamente
