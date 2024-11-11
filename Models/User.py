# models/user.py
from sqlalchemy import Column, Integer, String
from database import Base

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=True)
    name = Column(String, nullable= False)
    address = Column(String, nullable= False)
    cccd = Column(String, nullable= False)

    def __repr__(self):
        return f"<User(username='{self.username}', password='{self.password}')>"