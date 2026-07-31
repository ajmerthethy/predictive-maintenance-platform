from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.maintenance import MaintenanceTask
from app.models.alert import Alert
from app.models.prediction import Prediction
from app.models.user import User
from app.services.tenancy import get_owned_machine_or_404


router = APIRouter(
    prefix="/history",
    tags=["Machine History"]
)


@router.get("/machines/{machine_id}")
def get_machine_history(
    machine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    get_owned_machine_or_404(db, machine_id, current_user.account_id)

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