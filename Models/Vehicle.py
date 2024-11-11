from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from Models.User import User

class Vehicle(Base):
    __tablename__ = 'vehicles'
    
    id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String, unique=True, index=True, nullable=False)
    brand = Column(String)
    model = Column(String)
    year = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    owner = relationship("User", back_populates="vehicles")

User.vehicles = relationship("Vehicle", order_by=Vehicle.id, back_populates="owner")