from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.ml import model_loader
from app.models.prediction import Prediction
from app.models.sensor_reading import SensorReading
from app.services.model_performance import (
    MIN_OBSERVED_FAILURES_FOR_CONFIDENCE,
    evaluate_model_performance,
)

client = TestClient(app)


def _add_reading_and_prediction(
    db_session, machine, *, actual_failure, predicted, model_version, minute=0
):
    reading = SensorReading(
        machine_id=machine.id,
        timestamp=datetime(2026, 1, 1) + timedelta(minutes=minute),
        air_temperature=300.0,
        process_temperature=310.0,
        rotational_speed=1500,
        torque=40,
        tool_wear=10,
        failure=actual_failure,
    )
    db_session.add(reading)
    db_session.commit()
    db_session.refresh(reading)

    prediction = Prediction(
        machine_id=machine.id,
        prediction=predicted,
        probability=0.9 if predicted else 0.1,
        sensor_reading_id=reading.id,
        model_version=model_version,
    )
    db_session.add(prediction)
    db_session.commit()

    return reading, prediction


# -----------------------------
# NO DATA YET
# -----------------------------

def test_no_evaluable_predictions_returns_honest_empty_shape(machine, db_session):
    result = evaluate_model_performance(db_session, machine.account_id)

    assert result["evaluated_predictions"] == 0
    assert result["observed_failures"] == 0
    assert result["sufficient_data"] is False
    assert result["accuracy"] is None
    assert result["note"]


# -----------------------------
# CORRECTNESS OF THE COMPARISON
# -----------------------------

def test_evaluates_predictions_against_observed_outcomes(machine, db_session):
    version = model_loader.MODEL_VERSION

    # 2 correct (TP, TN), 1 wrong (FN: actual failure, predicted healthy).
    _add_reading_and_prediction(
        db_session, machine, actual_failure=True, predicted=1,
        model_version=version, minute=0,
    )
    _add_reading_and_prediction(
        db_session, machine, actual_failure=False, predicted=0,
        model_version=version, minute=1,
    )
    _add_reading_and_prediction(
        db_session, machine, actual_failure=True, predicted=0,
        model_version=version, minute=2,
    )

    result = evaluate_model_performance(db_session, machine.account_id)

    assert result["evaluated_predictions"] == 3
    assert result["observed_failures"] == 2
    assert result["accuracy"] == pytest.approx(2 / 3)

    # confusion_matrix(labels=[0,1]) -> [[TN, FP], [FN, TP]]
    assert result["confusion_matrix"] == [[1, 0], [1, 1]]


# -----------------------------
# SCOPING: only the current model version, only linked readings
# -----------------------------

def test_excludes_predictions_from_a_different_model_version(machine, db_session):
    current_version = model_loader.MODEL_VERSION

    _add_reading_and_prediction(
        db_session, machine, actual_failure=True, predicted=1,
        model_version="not-the-current-version", minute=0,
    )

    result = evaluate_model_performance(db_session, machine.account_id)
    assert result["evaluated_predictions"] == 0

    # But explicitly asking for that version finds it.
    result_for_old_version = evaluate_model_performance(
        db_session, machine.account_id, model_version="not-the-current-version"
    )
    assert result_for_old_version["evaluated_predictions"] == 1
    assert current_version != "not-the-current-version"


def test_excludes_predictions_with_no_linked_sensor_reading(machine, db_session):
    """POST /prediction/'s direct-input path has no sensor_reading_id -
    nothing to compare its prediction against, so it must not be counted.
    """
    prediction = Prediction(
        machine_id=machine.id,
        prediction=1,
        probability=0.9,
        sensor_reading_id=None,
        model_version=model_loader.MODEL_VERSION,
    )
    db_session.add(prediction)
    db_session.commit()

    result = evaluate_model_performance(db_session, machine.account_id)
    assert result["evaluated_predictions"] == 0


# -----------------------------
# sufficient_data THRESHOLD
# -----------------------------

def test_sufficient_data_false_below_threshold(machine, db_session):
    version = model_loader.MODEL_VERSION

    for i in range(MIN_OBSERVED_FAILURES_FOR_CONFIDENCE - 1):
        _add_reading_and_prediction(
            db_session, machine, actual_failure=True, predicted=1,
            model_version=version, minute=i,
        )

    result = evaluate_model_performance(db_session, machine.account_id)
    assert result["sufficient_data"] is False
    assert result["note"]


def test_sufficient_data_true_at_threshold(machine, db_session):
    version = model_loader.MODEL_VERSION

    for i in range(MIN_OBSERVED_FAILURES_FOR_CONFIDENCE):
        _add_reading_and_prediction(
            db_session, machine, actual_failure=True, predicted=1,
            model_version=version, minute=i,
        )

    result = evaluate_model_performance(db_session, machine.account_id)
    assert result["sufficient_data"] is True
    assert result["note"] is None


# -----------------------------
# END TO END
# -----------------------------

def test_model_performance_summary_endpoint(machine, db_session):
    _add_reading_and_prediction(
        db_session, machine, actual_failure=True, predicted=1,
        model_version=model_loader.MODEL_VERSION, minute=0,
    )

    response = client.get("/model-performance/summary")

    assert response.status_code == 200
    data = response.json()
    assert data["model_version"] == model_loader.MODEL_VERSION
    assert data["evaluated_predictions"] == 1
