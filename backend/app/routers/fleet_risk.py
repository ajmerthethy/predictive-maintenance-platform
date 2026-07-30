from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.risk_service import get_latest_prediction_by_machine


router = APIRouter(
    prefix="/fleet-risk",
    tags=["Fleet Risk"]
)


@router.get("/summary")
def fleet_risk_summary(
    db: Session = Depends(get_db)
):

    healthy = 0
    warning = 0
    critical = 0

    assets = []


    for machine, prediction in get_latest_prediction_by_machine(db):

        if not prediction:
            continue


        risk = prediction.probability * 100


        if risk >= 75:

            status = "Critical"
            critical += 1


        elif risk >= 50:

            status = "Warning"
            warning += 1


        else:

            status = "Healthy"
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
