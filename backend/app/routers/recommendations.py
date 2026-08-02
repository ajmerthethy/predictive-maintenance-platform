from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.services.maintenance_recommendation import (
    generate_maintenance_recommendation
)

from app.services.risk_service import calculate_risk_level, get_latest_prediction
from app.services.tenancy import get_owned_machine_or_404


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)


@router.get("/machines/{machine_id}")
def get_recommendation(
    machine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reads the most recently stored prediction - performs no inference
    and creates no new Prediction row (a GET must be read-only).
    """

    get_owned_machine_or_404(db, machine_id, current_user.account_id)

    prediction = get_latest_prediction(db, machine_id)

    if prediction is None:
        raise HTTPException(
            status_code=404,
            detail="No prediction available for this machine yet.",
        )

    risk_level = calculate_risk_level(prediction.probability)

    return generate_maintenance_recommendation(
        prediction.probability,
        risk_level
    )
