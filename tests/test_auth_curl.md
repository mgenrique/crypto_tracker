# 1. Registrar usuario
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "myuser",
    "password": "SecurePass123"
  }'

# 2. Login
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
# Response: {"access_token": "eyJ0...", "refresh_token": "eyJ0...", "token_type": "bearer"}

# 3. Usar token en request
curl -X GET "http://localhost:8000/api/v1/auth/profile" \
  -H "Authorization: Bearer eyJ0..."

# 4. Crear API key
curl -X POST "http://localhost:8000/api/v1/auth/api-keys" \
  -H "Authorization: Bearer eyJ0..." \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mobile App"
  }'

# 5. Listar API keys
curl -X GET "http://localhost:8000/api/v1/auth/api-keys" \
  -H "Authorization: Bearer eyJ0..."

# 6. Usar JWT en endpoints protegidos
curl -X GET "http://localhost:8000/api/v1/wallets" \
  -H "Authorization: Bearer eyJ0..."

# 7. Refreshar token
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJ0..."
  }'
