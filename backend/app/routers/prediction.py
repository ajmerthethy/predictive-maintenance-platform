
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.alert import Alert
from app.services.alert_service import generate_alert

router = APIRouter(
    prefix="/prediction",
    tags=["Prediction"]
)

from pydantic import BaseModel
from app.ml.predict import predict_failure
from app.ml.live_prediction import predict_failure_from_reading
from app.models.prediction import Prediction
from app.ml.explain import get_feature_importance

class PredictionRequest(BaseModel):
    air_temperature: float
    process_temperature: float
    rotational_speed: float
    torque: float
    tool_wear: float

@router.post("/")
def predict(
    request: PredictionRequest,
    machine_id: int,
    db: Session = Depends(get_db)
):

    result = predict_failure(
    air_temperature=request.air_temperature,
    process_temperature=request.process_temperature,
    rotational_speed=request.rotational_speed,
    torque=request.torque,
    tool_wear=request.tool_wear
)

    prediction_record = Prediction(
        machine_id=machine_id,
        prediction=result["prediction"],
        probability=result["probability"]
    )

    db.add(prediction_record)
    db.commit()
    db.refresh(prediction_record)

    alert_data = generate_alert(prediction_record)

    if alert_data:

        alert = Alert(
            machine_id=machine_id,
            probability=prediction_record.probability,
            severity=alert_data["severity"],
            message=alert_data["message"],
            recommended_action=alert_data["recommended_action"]
        )

        db.add(alert)
        db.commit()

    return {
        "machine_id": machine_id,
        "prediction": result["prediction"],
        "probability": result["probability"],
        "top_factors": result["top_factors"],
        "created_at": prediction_record.created_at
    }

@router.get("/machines/{machine_id}")
def predict_latest(machine_id: int, db: Session = Depends(get_db)):
    return predict_failure_from_reading(db, machine_id)

@router.get("/history/{machine_id}")
def prediction_history(machine_id: int, db: Session = Depends(get_db)):

    predictions = (
        db.query(Prediction)
        .filter(Prediction.machine_id == machine_id)
        .order_by(Prediction.created_at.asc())
        .all()
    )

    return predictions

@router.get("/explanation")
def explanation():

    return {
        "feature_importance": get_feature_importance()
    }