
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db

router = APIRouter(
    prefix="/prediction",
    tags=["Prediction"]
)
from pydantic import BaseModel

from app.ml.predict import predict_failure
from app.ml.live_prediction import predict_failure_from_reading

class PredictionRequest(BaseModel):
    temperature: float
    vibration: float
    pressure: float

@router.post("/")
def predict(request: PredictionRequest):

    result = predict_failure(
        temperature=request.temperature,
        vibration=request.vibration,
        pressure=request.pressure
    )

    return result

@router.get("/machines/{machine_id}")
def predict_latest(machine_id: int, db: Session = Depends(get_db)):
    return predict_failure_from_reading(db, machine_id)

