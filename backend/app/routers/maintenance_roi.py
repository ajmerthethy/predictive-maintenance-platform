from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.models.prediction import Prediction
from app.models.alert import Alert
from app.models.maintenance import MaintenanceTask

from app.services.health_score import (
    calculate_asset_health_score
)

from app.services.downtime_cost import (
    calculate_downtime_cost
)

from app.services.maintenance_roi import (
    calculate_maintenance_roi
)


router = APIRouter(
    prefix="/roi",
    tags=["Maintenance ROI"]
)


@router.get("/machines/{machine_id}")
def maintenance_roi(
    machine_id: int,
    db: Session = Depends(get_db)
):

    prediction = (
        db.query(Prediction)
        .filter(
            Prediction.machine_id == machine_id
        )
        .order_by(
            Prediction.created_at.desc()
        )
        .first()
    )

    if not prediction:

        raise HTTPException(
            status_code=404,
            detail="No prediction found."
        )

    active_alerts = (
        db.query(Alert)
        .filter(
            Alert.machine_id == machine_id,
            Alert.status != "RESOLVED"
        )
        .count()
    )

    open_work_orders = (
        db.query(MaintenanceTask)
        .filter(
            MaintenanceTask.machine_id == machine_id,
            MaintenanceTask.status != "COMPLETED"
        )
        .count()
    )

    if prediction.probability > 0.80:
        health_status = "Critical"

    elif prediction.probability > 0.50:
        health_status = "Warning"

    else:
        health_status = "Healthy"

    health = calculate_asset_health_score(
        failure_probability=prediction.probability,
        health_status=health_status,
        active_alerts=active_alerts,
        open_work_orders=open_work_orders
    )

    downtime = calculate_downtime_cost(
        health["rating"],
        health["health_score"]
    )

    return calculate_maintenance_roi(
        downtime_cost_per_day=downtime["estimated_daily_cost"],
        health_score=health["health_score"]
    )