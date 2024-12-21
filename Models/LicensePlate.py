from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base

class LicensePlate(Base):
    __tablename__ = 'license_plate'
    id = Column(Integer, primary_key=True, index=True)
    license_plate = Column(String, nullable=False)
    time = Column(DateTime, nullable=False)
    image_path = Column(String, nullable=False)