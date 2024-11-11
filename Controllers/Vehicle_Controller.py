# controllers/vehicle_controller.py
from Models.Vehicle import Vehicle
from database import get_db
from sqlalchemy.orm import Session

def create_vehicle(license_plate: str, brand: str, model: str, year: int, user_id: int, db: Session):
    db_vehicle = Vehicle(license_plate=license_plate, brand=brand, model=model, year=year, user_id=user_id)
    db.add(db_vehicle)
    db.commit()
    db.refresh(db_vehicle)
    return db_vehicle

def get_vehicles_by_user(user_id: int, db: Session):
    return db.query(Vehicle).filter(Vehicle.user_id == user_id).all()