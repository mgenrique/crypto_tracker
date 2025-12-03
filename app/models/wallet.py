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
