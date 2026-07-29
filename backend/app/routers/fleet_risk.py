from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.machine import Machine
from app.models.prediction import Prediction


router = APIRouter(
    prefix="/fleet-risk",
    tags=["Fleet Risk"]
)


@router.get("/summary")
def fleet_risk_summary(
    db: Session = Depends(get_db)
):

    machines = db.query(Machine).all()

    healthy = 0
    warning = 0
    critical = 0

    assets = []


    for machine in machines:

        prediction = (
            db.query(Prediction)
            .filter(
                Prediction.machine_id == machine.id
            )
            .order_by(
                Prediction.created_at.desc()
            )
            .first()
        )


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