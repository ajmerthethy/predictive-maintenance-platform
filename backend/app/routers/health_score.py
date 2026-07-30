from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.sensor_reading import SensorReading
from app.models.prediction import Prediction
from app.models.alert import Alert
from app.models.maintenance import MaintenanceTask

from app.services.health_score import calculate_asset_health_score
from app.services.risk_service import calculate_risk_level

router = APIRouter(
    prefix="/health-score",
    tags=["Asset Health Score"]
)


@router.get("/machines/{machine_id}")
def get_health_score(
    machine_id: int,
    db: Session = Depends(get_db)
):

    prediction = (
        db.query(Prediction)
        .filter(Prediction.machine_id == machine_id)
        .order_by(Prediction.created_at.desc())
        .first()
    )

    if not prediction:
        raise HTTPException(
            status_code=404,
            detail="Prediction not found."
        )

    reading = (
        db.query(SensorReading)
        .filter(SensorReading.machine_id == machine_id)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )

    if not reading:
        raise HTTPException(
            status_code=404,
            detail="Sensor reading not found."
        )

    health_status = calculate_risk_level(prediction.probability)

    active_alerts = (
        db.query(Alert)
        .filter(
            Alert.machine_id == machine_id,
            Alert.status != "RESOLVED",
        )
        .count()
    )

    open_work_orders = (
        db.query(MaintenanceTask)
        .filter(
            MaintenanceTask.machine_id == machine_id,
            MaintenanceTask.status != "COMPLETED",
        )
        .count()
    )

    return calculate_asset_health_score(
        failure_probability=prediction.probability,
        health_status=health_status,
        active_alerts=active_alerts,
        open_work_orders=open_work_orders,
    )