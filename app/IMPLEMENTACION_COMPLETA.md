# GUÍA COMPLETA DE IMPLEMENTACIÓN - Crypto Dashboard
## Código listo para copiar y pegar

---

## 📁 ESTRUCTURA DE CARPETAS FINAL

```
proyecto/
├── main.py                          # Punto de entrada FastAPI
├── cli.py                           # CLI interactivo
├── requirements.txt                 # Dependencias
├── .env.example                     # Variables de entorno
├── .env                             # Variables de entorno (local)
│
├── app/
│   ├── __init__.py
│   ├── config.py                    # Configuración
│   ├── database.py                  # Conexión a BD
│   ├── dependencies.py              # Dependencias compartidas
│   ├── security.py                  # JWT, hashing
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                  # Modelo User
│   │   ├── wallet.py                # Modelo Wallet
│   │   ├── exchange.py              # Modelo Exchange
│   │   ├── token.py                 # Modelo Token
│   │   ├── defi_position.py         # Modelo DeFi
│   │   └── transaction.py           # Modelo Transaction
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py                  # Schemas User
│   │   ├── wallet.py                # Schemas Wallet
│   │   ├── exchange.py              # Schemas Exchange
│   │   ├── token.py                 # Schemas Token
│   │   ├── defi.py                  # Schemas DeFi
│   │   └── portfolio.py             # Schemas Portfolio
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py                  # /auth endpoints
│   │   ├── wallets.py               # /wallets endpoints
│   │   ├── exchanges.py             # /exchanges endpoints
│   │   ├── tokens.py                # /tokens endpoints
│   │   ├── portfolio.py             # /portfolio endpoints
│   │   ├── defi.py                  # /defi endpoints
│   │   └── reports.py               # /reports endpoints
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── blockchain.py            # Web3 service
│   │   ├── exchange_service.py      # Binance/Kraken service
│   │   ├── token_service.py         # CoinGecko service
│   │   ├── portfolio_service.py     # Portfolio calculations
│   │   ├── cache_service.py         # Redis cache
│   │   ├── reports_service.py       # Reports generation
│   │   └── notification_service.py  # Email notifications
│   │
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── user.py                  # CRUD User
│   │   ├── wallet.py                # CRUD Wallet
│   │   ├── exchange.py              # CRUD Exchange
│   │   ├── token.py                 # CRUD Token
│   │   └── defi_position.py         # CRUD DeFi
│   │
│   └── utils/
│       ├── __init__.py
│       ├── validators.py            # Validaciones custom
│       ├── formatters.py            # Formateo de datos
│       └── constants.py             # Constantes
│
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_wallets.py
│   └── test_portfolio.py
│
└── logs/
    └── app.log
```

---

## 1️⃣ .env.example - Variables de entorno

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/crypto_dashboard
# Or for SQLite (development):
# DATABASE_URL=sqlite:///./crypto_dashboard.db

# JWT
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Server
DEBUG=True
API_V1_STR=/api/v1
PROJECT_NAME=Crypto Portfolio Dashboard

# Blockchain
WEB3_PROVIDER_URI=https://eth-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY
ARBITRUM_RPC=https://arb-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY
POLYGON_RPC=https://polygon-mainnet.g.alchemy.com/v2/YOUR_ALCHEMY_KEY

# Binance
BINANCE_API_KEY=your-binance-api-key
BINANCE_API_SECRET=your-binance-api-secret

# Redis
REDIS_URL=redis://localhost:6379

# Email
SENDGRID_API_KEY=your-sendgrid-api-key
ADMIN_EMAIL=admin@example.com

# Logging
LOG_LEVEL=INFO
```

---

## 2️⃣ app/config.py - Configuración

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./crypto_dashboard.db"
    
    # JWT
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Server
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Crypto Portfolio Dashboard"
    
    # Blockchain
    WEB3_PROVIDER_URI: str = "https://eth-mainnet.g.alchemy.com/v2/demo"
    ARBITRUM_RPC: str = "https://arb-mainnet.g.alchemy.com/v2/demo"
    POLYGON_RPC: str = "https://polygon-mainnet.g.alchemy.com/v2/demo"
    
    # Exchanges
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_API_SECRET: Optional[str] = None
    
    # Cache
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_EXPIRATION: int = 300
    
    # Email
    SENDGRID_API_KEY: Optional[str] = None
    ADMIN_EMAIL: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

---

## 3️⃣ app/database.py - Conexión a BD

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings

# Crear engine
if "sqlite" in settings.DATABASE_URL:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos
from sqlalchemy.orm import declarative_base
Base = declarative_base()

def get_db() -> Session:
    """Obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 4️⃣ app/security.py - Seguridad

```python
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config import settings
from app.database import get_db
from sqlalchemy.orm import Session

# Hash password
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def hash_password(password: str) -> str:
    """Hash de contraseña"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crear JWT token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_token(token: str = Depends(oauth2_scheme)) -> str:
    """Verificar y decodificar token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user_id
```

---

## 5️⃣ app/models/user.py - Modelo Usuario

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    wallets = relationship("Wallet", back_populates="owner")
    exchanges = relationship("Exchange", back_populates="owner")
    tokens = relationship("Token", back_populates="user")
    defi_positions = relationship("DefiPosition", back_populates="user")
```

---

## 6️⃣ app/models/wallet.py - Modelo Wallet

```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Wallet(Base):
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    address = Column(String, unique=True, index=True)
    network = Column(String)  # ethereum, arbitrum, polygon
    balance = Column(Float, default=0)
    verified = Column(Integer, default=0)  # 0=pending, 1=verified
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="wallets")
```

---

## 7️⃣ app/models/exchange.py - Modelo Exchange

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Exchange(Base):
    __tablename__ = "exchanges"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)  # binance, kraken, coinbase
    api_key = Column(String)
    api_secret = Column(String)  # Encriptado en producción
    balance = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="exchanges")
```

---

## 8️⃣ app/schemas/user.py - Schemas Usuario

```python
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    user_id: Optional[str] = None
```

---

## 9️⃣ app/schemas/wallet.py - Schemas Wallet

```python
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WalletCreate(BaseModel):
    name: str
    address: str
    network: str

class WalletUpdate(BaseModel):
    name: Optional[str] = None
    balance: Optional[float] = None

class WalletResponse(BaseModel):
    id: int
    name: str
    address: str
    network: str
    balance: float
    verified: int
    created_at: datetime
    
    class Config:
        from_attributes = True
```

---

## 🔟 app/crud/user.py - CRUD Usuario

```python
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.security import hash_password, verify_password

class UserCRUD:
    @staticmethod
    def create(db: Session, user: UserCreate) -> User:
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hash_password(user.password)
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> User:
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_by_id(db: Session, user_id: int) -> User:
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> User:
        user = UserCRUD.get_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

user_crud = UserCRUD()
```

---

## 1️⃣1️⃣ app/crud/wallet.py - CRUD Wallet

```python
from sqlalchemy.orm import Session
from app.models.wallet import Wallet
from app.schemas.wallet import WalletCreate, WalletUpdate

class WalletCRUD:
    @staticmethod
    def create(db: Session, user_id: int, wallet: WalletCreate) -> Wallet:
        db_wallet = Wallet(
            user_id=user_id,
            name=wallet.name,
            address=wallet.address,
            network=wallet.network
        )
        db.add(db_wallet)
        db.commit()
        db.refresh(db_wallet)
        return db_wallet
    
    @staticmethod
    def get_user_wallets(db: Session, user_id: int):
        return db.query(Wallet).filter(Wallet.user_id == user_id).all()
    
    @staticmethod
    def get_by_id(db: Session, wallet_id: int) -> Wallet:
        return db.query(Wallet).filter(Wallet.id == wallet_id).first()
    
    @staticmethod
    def update(db: Session, wallet_id: int, wallet_update: WalletUpdate) -> Wallet:
        db_wallet = WalletCRUD.get_by_id(db, wallet_id)
        if db_wallet:
            update_data = wallet_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(db_wallet, field, value)
            db.commit()
            db.refresh(db_wallet)
        return db_wallet
    
    @staticmethod
    def delete(db: Session, wallet_id: int) -> bool:
        db_wallet = WalletCRUD.get_by_id(db, wallet_id)
        if db_wallet:
            db.delete(db_wallet)
            db.commit()
            return True
        return False

wallet_crud = WalletCRUD()
```

---

## 1️⃣2️⃣ app/routes/auth.py - Endpoints Autenticación

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.crud.user import user_crud
from app.security import create_access_token, verify_token, hash_password
from app.config import settings
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=Token)
def register(user_create: UserCreate, db: Session = Depends(get_db)):
    """Registrar nuevo usuario"""
    existing = user_crud.get_by_email(db, user_create.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    user = user_crud.create(db, user_create)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }

@router.post("/login", response_model=Token)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """Login usuario"""
    user = user_crud.authenticate(db, user_login.email, user_login.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }

@router.get("/profile", response_model=UserResponse)
def get_profile(user_id: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Obtener perfil del usuario"""
    user = user_crud.get_by_id(db, int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/token", response_model=Token)
def token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2 compatible token endpoint"""
    user = user_crud.authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }
```

---

## 1️⃣3️⃣ app/routes/wallets.py - Endpoints Wallets

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.wallet import WalletCreate, WalletResponse, WalletUpdate
from app.crud.wallet import wallet_crud
from app.security import verify_token
from typing import List

router = APIRouter(prefix="/wallets", tags=["wallets"])

@router.get("", response_model=List[WalletResponse])
def list_wallets(user_id: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Listar wallets del usuario"""
    wallets = wallet_crud.get_user_wallets(db, int(user_id))
    return wallets

@router.post("", response_model=WalletResponse)
def create_wallet(
    wallet: WalletCreate,
    user_id: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Crear nueva wallet"""
    db_wallet = wallet_crud.create(db, int(user_id), wallet)
    return db_wallet

@router.get("/{wallet_id}", response_model=WalletResponse)
def get_wallet(wallet_id: int, user_id: str = Depends(verify_token), db: Session = Depends(get_db)):
    """Obtener wallet por ID"""
    wallet = wallet_crud.get_by_id(db, wallet_id)
    if not wallet or wallet.user_id != int(user_id):
        raise HTTPException(status_code=404, detail="Wallet not found")
    return wallet

@router.put("/{wallet_id}", response_model=WalletResponse)
def update_wallet(
    wallet_id: int,
    wallet_update: WalletUpdate,
    user_id: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Actualizar wallet"""
    wallet = wallet_crud.get_by_id(db, wallet_id)
    if not wallet or wallet.user_id != int(user_id):
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    updated = wallet_crud.update(db, wallet_id, wallet_update)
    return updated

@router.delete("/{wallet_id}")
def delete_wallet(
    wallet_id: int,
    user_id: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Eliminar wallet"""
    wallet = wallet_crud.get_by_id(db, wallet_id)
    if not wallet or wallet.user_id != int(user_id):
        raise HTTPException(status_code=404, detail="Wallet not found")
    
    success = wallet_crud.delete(db, wallet_id)
    if success:
        return {"message": "Wallet deleted"}
    raise HTTPException(status_code=400, detail="Could not delete wallet")
```

---

## 1️⃣4️⃣ app/services/blockchain.py - Servicio Web3

```python
from web3 import Web3
from app.config import settings
from typing import Optional

class BlockchainService:
    def __init__(self):
        self.eth_web3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URI))
        self.arb_web3 = Web3(Web3.HTTPProvider(settings.ARBITRUM_RPC))
        self.poly_web3 = Web3(Web3.HTTPProvider(settings.POLYGON_RPC))
    
    def get_balance(self, address: str, network: str = "ethereum") -> float:
        """Obtener balance en ETH"""
        if not Web3.is_address(address):
            raise ValueError("Invalid address")
        
        web3 = self._get_web3(network)
        balance_wei = web3.eth.get_balance(address)
        balance_eth = Web3.from_wei(balance_wei, 'ether')
        return float(balance_eth)
    
    def _get_web3(self, network: str) -> Web3:
        """Obtener instancia Web3 según red"""
        networks = {
            "ethereum": self.eth_web3,
            "arbitrum": self.arb_web3,
            "polygon": self.poly_web3
        }
        return networks.get(network.lower(), self.eth_web3)
    
    def is_valid_address(self, address: str) -> bool:
        """Validar dirección Ethereum"""
        return Web3.is_address(address)
    
    def get_token_balance(self, address: str, token_contract: str, network: str = "ethereum") -> float:
        """Obtener balance de token ERC20"""
        web3 = self._get_web3(network)
        
        # Simple ABI for ERC20 balanceOf
        abi = [{"constant": True, "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"}]
        
        contract = web3.eth.contract(address=token_contract, abi=abi)
        balance = contract.functions.balanceOf(address).call()
        return balance / 10**18  # Assuming 18 decimals

blockchain_service = BlockchainService()
```

---

## 1️⃣5️⃣ app/services/token_service.py - Servicio Tokens

```python
import requests
from typing import Dict, List, Optional
import asyncio

class TokenService:
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    @staticmethod
    def get_price(symbol: str) -> Optional[Dict]:
        """Obtener precio de token desde CoinGecko"""
        try:
            url = f"{TokenService.BASE_URL}/simple/price"
            params = {
                "ids": symbol.lower(),
                "vs_currencies": "usd",
                "include_market_cap": "true",
                "include_24hr_vol": "true",
                "include_24hr_change": "true"
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get(symbol.lower())
        except Exception as e:
            print(f"Error fetching price: {str(e)}")
            return None
    
    @staticmethod
    def get_prices_batch(symbols: List[str]) -> Dict:
        """Obtener múltiples precios"""
        prices = {}
        for symbol in symbols:
            price = TokenService.get_price(symbol)
            if price:
                prices[symbol] = price
        return prices
    
    @staticmethod
    def get_market_data(symbol: str) -> Optional[Dict]:
        """Obtener datos de mercado completos"""
        try:
            url = f"{TokenService.BASE_URL}/coins/{symbol.lower()}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error fetching market data: {str(e)}")
            return None

token_service = TokenService()
```

---

## 1️⃣6️⃣ app/services/exchange_service.py - Servicio Exchanges

```python
from binance.client import Client
from app.config import settings
from typing import Optional, Dict, List

class ExchangeService:
    def __init__(self):
        if settings.BINANCE_API_KEY and settings.BINANCE_API_SECRET:
            self.binance_client = Client(
                api_key=settings.BINANCE_API_KEY,
                api_secret=settings.BINANCE_API_SECRET
            )
        else:
            self.binance_client = None
    
    def get_account_balance(self) -> Optional[Dict]:
        """Obtener balance de cuenta Binance"""
        if not self.binance_client:
            return None
        
        try:
            account = self.binance_client.get_account()
            balances = {b['asset']: float(b['free']) for b in account['balances']}
            return balances
        except Exception as e:
            print(f"Error fetching balance: {str(e)}")
            return None
    
    def get_exchange_info(self) -> Optional[Dict]:
        """Obtener información de exchange"""
        if not self.binance_client:
            return None
        
        try:
            return self.binance_client.get_exchange_info()
        except Exception as e:
            print(f"Error fetching exchange info: {str(e)}")
            return None
    
    def get_ticker(self, symbol: str) -> Optional[Dict]:
        """Obtener ticker de símbolo"""
        if not self.binance_client:
            return None
        
        try:
            return self.binance_client.get_symbol_info(symbol)
        except Exception as e:
            print(f"Error fetching ticker: {str(e)}")
            return None

exchange_service = ExchangeService()
```

---

## 1️⃣7️⃣ app/services/portfolio_service.py - Servicio Portfolio

```python
from sqlalchemy.orm import Session
from app.models.wallet import Wallet
from app.models.exchange import Exchange
from app.services.blockchain import blockchain_service
from app.services.token_service import token_service
from typing import Dict, Optional

class PortfolioService:
    @staticmethod
    def get_portfolio_summary(user_id: int, db: Session) -> Dict:
        """Obtener resumen de portfolio"""
        wallets = db.query(Wallet).filter(Wallet.user_id == user_id).all()
        exchanges = db.query(Exchange).filter(Exchange.user_id == user_id).all()
        
        total_balance = 0
        wallet_data = []
        
        # Calcular balance de wallets
        for wallet in wallets:
            try:
                balance = blockchain_service.get_balance(wallet.address, wallet.network)
                wallet.balance = balance
                total_balance += balance
                wallet_data.append({
                    "id": wallet.id,
                    "name": wallet.name,
                    "address": wallet.address,
                    "network": wallet.network,
                    "balance": balance
                })
            except Exception as e:
                print(f"Error fetching balance for {wallet.address}: {str(e)}")
        
        # Calcular balance de exchanges
        exchange_data = []
        for exchange in exchanges:
            exchange_balances = exchange_service.get_account_balance()
            if exchange_balances:
                exchange_total = sum(exchange_balances.values())
                total_balance += exchange_total
                exchange_data.append({
                    "id": exchange.id,
                    "name": exchange.name,
                    "balance": exchange_total
                })
        
        return {
            "total_balance": total_balance,
            "wallets": wallet_data,
            "exchanges": exchange_data,
            "wallet_count": len(wallets),
            "exchange_count": len(exchanges)
        }
    
    @staticmethod
    def get_asset_allocation(user_id: int, db: Session) -> Dict:
        """Obtener asignación de activos"""
        summary = PortfolioService.get_portfolio_summary(user_id, db)
        
        allocation = {
            "wallets": {
                "percentage": 0,
                "value": 0
            },
            "exchanges": {
                "percentage": 0,
                "value": 0
            }
        }
        
        total = summary['total_balance']
        if total > 0:
            wallet_value = sum(w['balance'] for w in summary['wallets'])
            exchange_value = sum(e['balance'] for e in summary['exchanges'])
            
            allocation['wallets']['value'] = wallet_value
            allocation['wallets']['percentage'] = (wallet_value / total) * 100
            allocation['exchanges']['value'] = exchange_value
            allocation['exchanges']['percentage'] = (exchange_value / total) * 100
        
        return allocation

portfolio_service = PortfolioService()
```

---

## 1️⃣8️⃣ main.py - Punto de entrada FastAPI

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import Base, engine
from app.routes import auth, wallets

# Crear tablas
Base.metadata.create_all(bind=engine)

# Crear app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(wallets.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "Crypto Dashboard API", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
```

---

## 📦 Instalación y uso

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar .env
cp .env.example .env
# Editar .env con tus configuraciones

# 3. Crear base de datos
python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"

# 4. Ejecutar servidor
python main.py

# 5. En otra terminal, ejecutar CLI
python cli.py

# 6. Acceder a documentación
# http://localhost:8000/docs
```

---

## 🎯 PRÓXIMAS FASES

Después de implementar esto:

1. **Fase 2**: Agregar más rutas (tokens, exchanges, defi, portfolio)
2. **Fase 3**: Servicios avanzados (cache Redis, reportes)
3. **Fase 4**: WebSockets para actualizaciones en tiempo real
4. **Fase 5**: Tests unitarios y E2E
5. **Fase 6**: Documentación y deployment

¡Todo el código está listo para copiar y pegar! 🚀
