
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.analytics.feature_engineering import create_sensor_features

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"]
)

@router.get("/machines/{machine_id}/features")
def get_machine_features(
    machine_id: int,
    db: Session = Depends(get_db)
):
    df = create_sensor_features(db, machine_id)

    if df.empty:
        return {"message": "No sensor readings found for this machine."}
    return df.to_dict(orient="records")