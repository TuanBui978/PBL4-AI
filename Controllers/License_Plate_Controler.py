from Models.LicensePlate import LicensePlate
from database import get_db
from sqlalchemy.orm import Session
from datetime import datetime as DateTime

def add_license_plate(plate: str, time: DateTime, image_path: str, db: Session = None):
    if db is None:
        db = next(get_db())
    db_license_plate = LicensePlate(license_plate = plate, time = time, image_path = image_path)
    db.add(db_license_plate)
    db.commit()
    db.refresh(db_license_plate)
    return db_license_plate
def get_all_license_plate(db: Session = None):
    if db is None:
        db = next(get_db())
    return db.query(LicensePlate).all()
def get_license_plate_by_plate_num(plate, db: Session = None):
    if db is None:
        db = next(get_db())
    return db.query(LicensePlate).filter(LicensePlate.license_plate.like(f"%{plate}%")).all()
def get_license_plate_by_id(id, db: Session = next(get_db())):
    return db.query(LicensePlate).filter(LicensePlate.id == id).first()
def get_license_plate_by_date_range(from_date, to_date):
    db = next(get_db())  # Lấy kết nối cơ sở dữ liệu
    try:
        # Thực hiện truy vấn tìm biển số trong khoảng thời gian
        results = db.query(LicensePlate).filter(
            LicensePlate.time >= from_date,
            LicensePlate.time <= to_date
        ).all()
        return results
    except Exception as e:
        print(f"Lỗi truy vấn: {e}")
        return []

