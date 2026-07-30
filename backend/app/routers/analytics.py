
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.models.prediction import Prediction
from app.services.risk_service import (
    get_latest_prediction_by_machine,
    calculate_risk_level,
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

@router.get("/summary")
def analytics_summary(
    db: Session = Depends(get_db)
):

    total_predictions = (
        db.query(Prediction)
        .count()
    )

    failures_detected = (
        db.query(Prediction)
        .filter(Prediction.prediction == 1)
        .count()
    )

    average_probability = (
        db.query(func.avg(Prediction.probability))
        .scalar()
    )

    high_risk_predictions = (
        db.query(Prediction)
        .filter(Prediction.probability >= 0.75)
        .count()
    )

    return {
        "total_predictions": total_predictions,
        "failures_detected": failures_detected,
        "average_failure_probability": round(
            float(average_probability or 0),
            3
        ),
        "high_risk_predictions": high_risk_predictions
    }

@router.get("/machines/risk")
def machine_risk_ranking(
    db: Session = Depends(get_db)
):

    results = []

    for machine, latest_prediction in get_latest_prediction_by_machine(db):

        if latest_prediction:

            probability = latest_prediction.probability
            risk_level = calculate_risk_level(probability)

            results.append(
                {
                    "machine_id": machine.id,
                    "machine_name": machine.name,
                    "failure_probability": probability,
                    "risk_level": risk_level,
                    "last_prediction": latest_prediction.created_at
                }
            )


    results.sort(
        key=lambda x: x["failure_probability"],
        reverse=True
    )

    return results
