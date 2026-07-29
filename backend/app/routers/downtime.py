from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.models.machine import Machine
from app.models.prediction import Prediction
from app.services.downtime_cost import calculate_downtime_cost
from app.services.health_score import calculate_asset_health_score


router = APIRouter(
    prefix="/downtime",
    tags=["Downtime"]
)


@router.get("/machines/{machine_id}")
def downtime_cost(
    machine_id: int,
    db: Session = Depends(get_db)
):

    machine = (
        db.query(Machine)
        .filter(
            Machine.id == machine_id
        )
        .first()
    )


    if not machine:

        raise HTTPException(
            status_code=404,
            detail="Machine not found"
        )


    latest_prediction = (
        db.query(Prediction)
        .filter(
            Prediction.machine_id == machine_id
        )
        .order_by(
            Prediction.created_at.desc()
        )
        .first()
    )


    if not latest_prediction:

        raise HTTPException(
            status_code=404,
            detail="No prediction found"
        )


    failure_probability = (
        latest_prediction.probability
    )


    # Determine status
    if failure_probability >= 0.8:
        status = "Critical"

    elif failure_probability >= 0.5:
        status = "Warning"

    else:
        status = "Healthy"



    health = calculate_asset_health_score(
        failure_probability,
        status
    )


    return calculate_downtime_cost(
        status,
        health["health_score"]
    )