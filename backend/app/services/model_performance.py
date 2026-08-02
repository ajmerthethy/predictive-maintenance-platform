from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from app.models.machine import Machine
from app.models.prediction import Prediction
from app.models.sensor_reading import SensorReading
from app.ml import model_loader

# Below this many *observed failures*, precision/recall/F1 are computed
# from too little signal to mean anything (e.g. a single false negative
# would swing recall from 100% to 0%) - the report still returns the
# numbers, but flags them rather than implying false confidence.
MIN_OBSERVED_FAILURES_FOR_CONFIDENCE = 5


def evaluate_model_performance(db, account_id, model_version=None):
    """Compares the model's binary prediction against the actual outcome
    recorded on the sensor reading it was computed from (SensorReading.
    failure - see app.schemas.sensor_reading.SensorReadingCreate.failure),
    for one account and one model version.

    Only predictions with a linked sensor_reading_id are evaluable (POST
    /prediction/'s direct-input path has nothing to compare against).
    Defaults to the currently active model version - comparing a
    since-replaced model's old predictions would answer "how did an old
    model do," not "how is the model doing now."
    """

    version = model_version or model_loader.MODEL_VERSION

    rows = (
        db.query(Prediction.prediction, SensorReading.failure)
        .join(Machine, Prediction.machine_id == Machine.id)
        .join(SensorReading, Prediction.sensor_reading_id == SensorReading.id)
        .filter(
            Machine.account_id == account_id,
            Prediction.model_version == version,
        )
        .all()
    )

    evaluated_predictions = len(rows)

    if evaluated_predictions == 0:
        return {
            "model_version": version,
            "evaluated_predictions": 0,
            "observed_failures": 0,
            "sufficient_data": False,
            "accuracy": None,
            "precision": None,
            "recall": None,
            "f1_score": None,
            "confusion_matrix": None,
            "note": (
                "No predictions with a linked sensor reading and a "
                "recorded outcome exist yet for this model version."
            ),
        }

    y_pred = [int(row[0]) for row in rows]
    y_true = [int(row[1]) for row in rows]

    observed_failures = sum(y_true)
    sufficient_data = observed_failures >= MIN_OBSERVED_FAILURES_FOR_CONFIDENCE

    note = None
    if not sufficient_data:
        note = (
            f"Only {observed_failures} observed failure(s) recorded so "
            "far for this model version - these metrics are not "
            "statistically meaningful yet. Mark a sensor reading's "
            "`failure` field true (single reading or the optional bulk "
            "CSV column) as real outcomes become known."
        )

    return {
        "model_version": version,
        "evaluated_predictions": evaluated_predictions,
        "observed_failures": observed_failures,
        "sufficient_data": sufficient_data,
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1_score": float(f1_score(y_true, y_pred, zero_division=0)),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=[0, 1]).tolist(),
        "note": note,
    }
