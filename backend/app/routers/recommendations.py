from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.services.maintenance_recommendation import (
    generate_maintenance_recommendation
)

from app.routers.prediction import (
    predict_failure_from_reading
)
from app.services.risk_service import calculate_risk_level
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

    get_owned_machine_or_404(db, machine_id, current_user.account_id)

    prediction = predict_failure_from_reading(
        db,
        machine_id
    )


    health_status = "Unknown"


    if prediction:

        probability = prediction["probability"]

        health_status = calculate_risk_level(probability)



    return generate_maintenance_recommendation(
        prediction["probability"],
        health_status
    )