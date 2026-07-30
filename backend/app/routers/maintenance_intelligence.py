from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.db.database import get_db
from app.models.prediction import Prediction


router = APIRouter(
    prefix="/maintenance-intelligence",
    tags=["Maintenance Intelligence"]
)


@router.get("/summary")
def maintenance_intelligence(
    db: Session = Depends(get_db)
):

    critical_assets = {}

    predictions = (
        db.query(Prediction)
        .options(joinedload(Prediction.machine))
        .order_by(
            Prediction.probability.desc()
        )
        .limit(5)
        .all()
    )


    for prediction in predictions:

        machine = prediction.machine

        if prediction.probability >= 0.5:

            risk = round(
                prediction.probability * 100,
                1
            )


            if (
                machine.name not in critical_assets
                or risk > critical_assets[machine.name]["risk"]
            ):

                critical_assets[machine.name] = {
                    "machine_name": machine.name,
                    "risk": risk,
                    "recommendation":
                        "Immediate inspection required"
                        if prediction.probability >= 0.8
                        else
                        "Schedule preventive maintenance"
                }


    return {
        "actions_required": list(
            critical_assets.values()
        )
    }
