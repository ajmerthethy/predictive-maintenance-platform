from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.services.risk_service import (
    get_latest_prediction_by_machine,
    calculate_risk_level,
)


router = APIRouter(
    prefix="/fleet-risk",
    tags=["Fleet Risk"]
)


@router.get("/summary")
def fleet_risk_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    healthy = 0
    warning = 0
    critical = 0

    assets = []


    for machine, prediction in get_latest_prediction_by_machine(
        db, current_user.account_id
    ):

        if not prediction:
            continue


        risk = prediction.probability * 100
        status = calculate_risk_level(prediction.probability)

        if status == "CRITICAL":
            critical += 1

        elif status == "WARNING":
            warning += 1

        else:
            healthy += 1


        assets.append(
            {
                "machine_id": machine.id,
                "machine_name": machine.name,
                "risk": round(risk,1),
                "status": status
            }
        )


    assets = sorted(
        assets,
        key=lambda x: x["risk"],
        reverse=True
    )


    return {

        "distribution": {
            "healthy": healthy,
            "warning": warning,
            "critical": critical
        },

        "assets": assets

    }
