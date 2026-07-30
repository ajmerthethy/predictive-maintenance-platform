from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.maintenance_recommendation import (
    generate_maintenance_recommendation
)

from app.routers.prediction import (
    predict_failure_from_reading
)
from app.services.risk_service import calculate_risk_level


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)


@router.get("/machines/{machine_id}")
def get_recommendation(
    machine_id: int,
    db: Session = Depends(get_db)
):

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