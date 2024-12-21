from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable = False)
    username = Column(String, nullable = False)
    password = Column(String, nullable = False)
    license_plate = Column(String, nullable=True)
    address = Column(String, nullable=True)
    cccd = Column(String, nullable=False)
    amount = Column(Integer, nullable=True)
    
    