from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.sensor_reading import SensorReading
from app.schemas.sensor_reading import (
    SensorReadingCreate,
    SensorReadingResponse
)

router = APIRouter(
    prefix = "/sensor_readings",
    tags = ["sensor_readings"]
)

@router.post("/", response_model=SensorReadingResponse)

def create_sensor_reading(
    reading: SensorReadingCreate,
    db: Session = Depends(get_db)
):
    db_sensor_reading = SensorReading(
        machine_id=reading.machine_id,
        timestamp=reading.timestamp,
        temperature=reading.temperature,
        vibration=reading.vibration,
        pressure=reading.pressure
    )

    db.add(db_sensor_reading)
    db.commit()
    db.refresh(db_sensor_reading)

    return db_sensor_reading

@router.get("/{machine_id}", response_model=list[SensorReadingResponse])
def get_sensor_readings(
    machine_id: int,
    db: Session = Depends(get_db)
):
    readings = (
        db.query(SensorReading)
        .filter(SensorReading.machine_id == machine_id)
        .all()
    )

    return readings