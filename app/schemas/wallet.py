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
