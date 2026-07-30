from sqlalchemy import func, select
from sqlalchemy.orm import aliased

from app.models.machine import Machine
from app.models.prediction import Prediction


def calculate_risk_level(probability):

    if probability >= 0.75:
        return "CRITICAL"

    elif probability >= 0.50:
        return "WARNING"

    return "LOW"


def get_latest_prediction_by_machine(db):
    """
    Returns a list of (Machine, Prediction | None) tuples: every machine
    paired with its single most recent prediction, in one query instead of
    one query per machine.
    """

    row_number = (
        func.row_number()
        .over(
            partition_by=Prediction.machine_id,
            order_by=Prediction.created_at.desc(),
        )
        .label("row_number")
    )

    latest_predictions = select(Prediction, row_number).subquery()

    LatestPrediction = aliased(Prediction, latest_predictions)

    return (
        db.query(Machine, LatestPrediction)
        .outerjoin(
            latest_predictions,
            (latest_predictions.c.machine_id == Machine.id)
            & (latest_predictions.c.row_number == 1),
        )
        .all()
    )
