from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.maintenance import MaintenanceTask
from app.models.alert import Alert
from app.models.prediction import Prediction


router = APIRouter(
    prefix="/history",
    tags=["Machine History"]
)


@router.get("/machines/{machine_id}")
def get_machine_history(
    machine_id: int,
    db: Session = Depends(get_db)
):

    maintenance = (
        db.query(MaintenanceTask)
        .filter(
            MaintenanceTask.machine_id == machine_id
        )
        .order_by(
            MaintenanceTask.created_at.desc()
        )
        .all()
    )


    alerts = (
        db.query(Alert)
        .filter(
            Alert.machine_id == machine_id
        )
        .order_by(
            Alert.created_at.desc()
        )
        .all()
    )


    predictions = (
        db.query(Prediction)
        .filter(
            Prediction.machine_id == machine_id
        )
        .order_by(
            Prediction.created_at.desc()
        )
        .all()
    )


    return {
        "maintenance": [
            {
                "date": task.created_at,
                "description": task.description,
                "status": task.status
            }
            for task in maintenance
        ],

        "alerts": [
            {
                "date": alert.created_at,
                "severity": alert.severity,
                "message": alert.message,
                "status": alert.status
            }
            for alert in alerts
        ],

        "predictions": [
            {
                "date": prediction.created_at,
                "probability": prediction.probability
            }
            for prediction in predictions
        ]
    }