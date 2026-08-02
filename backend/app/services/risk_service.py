from sqlalchemy import func, select
from sqlalchemy.orm import aliased

from app.models.machine import Machine
from app.models.prediction import Prediction

# The single source of truth for probability -> risk tier. Every other
# place in the backend and dashboard that needs to classify a failure
# probability must call calculate_risk_level() (or, for a SQL filter that
# can't call a Python function, reference these constants) rather than
# re-deriving its own cutoffs - see the ML/MLOps audit's Part 7 finding on
# four independent, inconsistent risk-classification implementations.
CRITICAL_THRESHOLD = 0.75
WARNING_THRESHOLD = 0.50


def calculate_risk_level(probability):

    if probability >= CRITICAL_THRESHOLD:
        return "CRITICAL"

    elif probability >= WARNING_THRESHOLD:
        return "WARNING"

    return "LOW"


def get_latest_prediction(db, machine_id):
    """The single most recent Prediction for one machine, or None. Shared
    by every endpoint that displays "the current prediction" without
    re-running inference (health_score, prediction, recommendations).
    """

    return (
        db.query(Prediction)
        .filter(Prediction.machine_id == machine_id)
        .order_by(Prediction.created_at.desc())
        .first()
    )


def get_latest_prediction_by_machine(db, account_id):
    """
    Returns a list of (Machine, Prediction | None) tuples: every machine
    belonging to `account_id`, paired with its single most recent
    prediction, in one query instead of one query per machine.
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
        .filter(Machine.account_id == account_id)
        .outerjoin(
            latest_predictions,
            (latest_predictions.c.machine_id == Machine.id)
            & (latest_predictions.c.row_number == 1),
        )
        .all()
    )
