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
