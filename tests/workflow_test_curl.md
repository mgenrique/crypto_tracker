# 1. REGISTRO
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"myuser","password":"SecurePass123"}'

# Response: ✅ User registered

# 2. LOGIN
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"SecurePass123"}'

# Response: {"access_token":"eyJ0...","refresh_token":"eyJ0...","token_type":"bearer","user":{...}}

# 3. CREAR WALLET (CON AUTENTICACIÓN)
curl -X POST "http://localhost:8000/api/v1/wallets" \
  -H "Authorization: Bearer eyJ0..." \
  -H "Content-Type: application/json" \
  -d '{"address":"0x742d35...","wallet_type":"hot","network":"ethereum","label":"Mi Wallet"}'

# 4. CREAR API KEY PARA INTEGRACIÓN
curl -X POST "http://localhost:8000/api/v1/auth/api-keys" \
  -H "Authorization: Bearer eyJ0..." \
  -H "Content-Type: application/json" \
  -d '{"name":"Mobile App"}'

# Response: {"key":"sk_...","secret":"...","name":"Mobile App","created_at":"2025-12-02T..."}

# 5. CONECTAR BINANCE
# (En settings de usuario - Próximo)

# 6. GENERAR REPORTE
curl -X GET "http://localhost:8000/api/v1/reports/portfolio" \
  -H "Authorization: Bearer eyJ0..."

# Response: Portfolio completo con datos reales de Binance
