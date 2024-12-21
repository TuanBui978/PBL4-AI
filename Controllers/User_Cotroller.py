from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from Models.User import User
from database import get_db
import bcrypt

def create_user(name: str, username: str, password: str, cccd: str, address: str = None, amount: int = None, db: Session = None):
    if db is None:
        db = next(get_db())

    # Kiểm tra username đã tồn tại chưa
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        return None

    # Mã hóa mật khẩu trước khi lưu
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Tạo user mới
    new_user = User(
        name=name,
        username=username,
        password=hashed_password,
        cccd=cccd,
        address=address,
        amount=amount
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def login_user(username: str, password: str, db: Session = None):
    if db is None:
        db = next(get_db())

    user = db.query(User).filter(User.username == username).first()
    if not user:
        return None

    stored_hashed_password = user.password
    if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
        return user
    else:
        return None

def get_user_by_id(user_id: int, db: Session = None):
    if db is None:
        db = next(get_db())

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return None

    return user