
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.sensor_reading import SensorReading
from app.models.user import User
from app.services.health_monitor import (
    calculate_health_status,
    analyze_sensor_trend
)
from app.services.tenancy import get_owned_machine_or_404

router = APIRouter(
    prefix="/machines",
    tags=["Health Monitoring"]
)

@router.get("/{machine_id}/health")
def get_machine_health(
    machine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    get_owned_machine_or_404(db, machine_id, current_user.account_id)

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
        air_temperature=reading.air_temperature,
        process_temperature=reading.process_temperature,
        rotational_speed=reading.rotational_speed,
        torque=reading.torque,
        tool_wear=reading.tool_wear
    )


    return {
        "machine_id": machine_id,
        **health
    }

@router.get("/{machine_id}/trend")
def get_machine_trend(
    machine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    get_owned_machine_or_404(db, machine_id, current_user.account_id)

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