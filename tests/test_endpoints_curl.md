# Test crear cartera
curl -X POST "http://localhost:8000/api/v1/wallets" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "0x742d35Cc6634C0532925a3b844Bc0e8e15b51d93",
    "wallet_type": "hot",
    "network": "ethereum",
    "label": "Mi Cartera"
  }'

# Test listar carteras
curl -X GET "http://localhost:8000/api/v1/wallets"

# Test registrar transacción
curl -X POST "http://localhost:8000/api/v1/wallets/1/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "tx_hash": "0xabc123...",
    "tx_type": "buy",
    "token_in": "USDC",
    "token_out": "ETH",
    "amount_in": "1000",
    "amount_out": "0.5",
    "price_usd_in": "1.0",
    "price_usd_out": "2000.0"
  }'

# Test portfolio summary
curl -X GET "http://localhost:8000/api/v1/portfolio/summary"

# Test calcular impuestos FIFO
curl -X POST "http://localhost:8000/api/v1/wallets/1/taxes/fifo?year=2024"

# Test reporte de portfolio
curl -X GET "http://localhost:8000/api/v1/reports/portfolio"

# Test reporte de impuestos
curl -X GET "http://localhost:8000/api/v1/reports/taxes?wallet_id=1&year=2024"

# Acceder a documentación interactiva
# http://localhost:8000/docs
# http://localhost:8000/redoc
