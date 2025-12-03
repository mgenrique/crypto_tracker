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
