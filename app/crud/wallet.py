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
