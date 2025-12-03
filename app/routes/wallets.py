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
