from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db

from app.models.prediction import Prediction
from app.models.user import User
from app.services.downtime_cost import calculate_downtime_cost
from app.services.health_score import calculate_asset_health_score
from app.services.risk_service import calculate_risk_level
from app.services.tenancy import get_owned_machine_or_404


router = APIRouter(
    prefix="/downtime",
    tags=["Downtime"]
)


@router.get("/machines/{machine_id}")
def downtime_cost(
    machine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    get_owned_machine_or_404(db, machine_id, current_user.account_id)

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


    status = calculate_risk_level(failure_probability)



    health = calculate_asset_health_score(
        failure_probability,
        status
    )


    return calculate_downtime_cost(
        status,
        health["health_score"]
    )