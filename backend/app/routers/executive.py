from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.prediction import Prediction
from app.models.alert import Alert
from sqlalchemy import distinct

from app.db.database import get_db

from app.models.machine import Machine
from app.models.maintenance import MaintenanceTask

from app.services.executive_analytics import (
    calculate_maintenance_compliance
)
from app.core.config import (
    DOWNTIME_EXPOSURE_PER_CRITICAL_MACHINE,
    POTENTIAL_SAVINGS_PER_CRITICAL_MACHINE,
)

router = APIRouter(
    prefix="/executive",
    tags=["Executive Dashboard"]
)

@router.get("/summary")
def executive_summary(
    db: Session = Depends(get_db)
):
    assets = db.query(Machine).count()

    open_work_orders = (
        db.query(MaintenanceTask)
        .filter(
            MaintenanceTask.status != "COMPLETED"
        )
        .count()
    )

    completed_work_orders = (
        db.query(MaintenanceTask)
        .filter(
            MaintenanceTask.status == "COMPLETED"
        )
        .count()
    )

    critical_assets = (
        db.query(
            distinct(Prediction.machine_id)
        )
        .filter(
            Prediction.prediction == 1
        )
        .count()
    )

    active_alerts = (
        db.query(Alert)
        .filter(
            Alert.status != "RESOLVED"
        )
        .count()
    )

    total_work_orders = (
        db.query(MaintenanceTask)
        .count()
    )

    maintenance_compliance = (
        calculate_maintenance_compliance(
            completed_work_orders,
            total_work_orders
        )
    )

    # -----------------------------
    # FLEET HEALTH SCORE
    # -----------------------------

    predictions = db.query(Prediction).all()

    scores = []

    for prediction in predictions:

        score = 100 - (
            prediction.probability * 100
        )

        scores.append(score)


    fleet_health_score = round(
        sum(scores) / len(scores),
        1
    ) if scores else 100

    # -----------------------------
    # DOWNTIME EXPOSURE
    # -----------------------------

    downtime_exposure = 0

    critical_machine_ids = set()

    for prediction in predictions:

        if prediction.prediction == 1:

            critical_machine_ids.add(
                prediction.machine_id
            )


    downtime_exposure = (
        len(critical_machine_ids) * DOWNTIME_EXPOSURE_PER_CRITICAL_MACHINE
    )

    # -----------------------------
    # POTENTIAL SAVINGS
    # -----------------------------

    potential_savings = 0

    for prediction in predictions:

        if prediction.prediction == 1:

            potential_savings = (
                len(critical_machine_ids) * POTENTIAL_SAVINGS_PER_CRITICAL_MACHINE
            )

    return {
        "assets": assets,
        "open_work_orders": open_work_orders,
        "maintenance_compliance": maintenance_compliance,
        "fleet_health_score": fleet_health_score,
        "critical_assets": critical_assets,
        "downtime_exposure": downtime_exposure,
        "potential_savings": potential_savings,
        "active_alerts": active_alerts,
    }