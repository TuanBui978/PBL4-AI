from Models.User import User
from database import get_db
from sqlalchemy.orm import Session

def create_user(username: str, password: str, name: str, address: str, cccd: str, db: Session):
    db_user = User(username=username, password=password, role = "user", name = name, address = address, cccd = cccd)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(username: str, db: Session):
    return db.query(User).filter(User.username == username).first()

