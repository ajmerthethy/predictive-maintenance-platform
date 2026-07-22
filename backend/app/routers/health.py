
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.sensor_reading import SensorReading
from app.services.health_monitor import calculate_health_status

from app.services.health_monitor import (
    calculate_health_status,
    analyze_sensor_trend
)

router = APIRouter(
    prefix="/machines",
    tags=["Health Monitoring"]
)

@router.get("/{machine_id}/health")
def get_machine_health(
    machine_id: int,
    db: Session = Depends(get_db)
):

    # Fetch the latest sensor readings for the machine
    reading = (
        db.query(SensorReading)
        .filter(SensorReading.machine_id == machine_id)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )

    if not reading:
        raise HTTPException(status_code=404, detail="No sensor readings found for this machine.")

    health = calculate_health_status(
        temperature=reading.temperature,
        vibration=reading.vibration,
        pressure=reading.pressure
    )


    return {
        "machine_id": machine_id,
        **health
    }

@router.get("/{machine_id}/trend")
def get_machine_trend(
    machine_id: int,
    db: Session = Depends(get_db)
):

    readings = (
        db.query(SensorReading)
        .filter(SensorReading.machine_id == machine_id)
        .order_by(SensorReading.timestamp.asc())
        .limit(100)  # Limit to the last 100 readings for trend analysis
        .all()
    )

    if not readings:
        raise HTTPException(status_code=404, detail="No sensor readings found for this machine.")

    trend = analyze_sensor_trend(readings)

    return {
        "machine_id": machine_id,
        **trend
    }