from fastapi.testclient import TestClient

from app.main import app
from app.models.prediction import Prediction

client = TestClient(app)


def _prediction_count(db_session, machine_id):
    return (
        db_session.query(Prediction)
        .filter(Prediction.machine_id == machine_id)
        .count()
    )


def _create_prediction(machine_id, probability_hint="critical"):
    """POST /prediction/ with sensor values verified elsewhere
    (test_alert_delivery.py) to produce a CRITICAL-range or healthy-range
    prediction from the real model.
    """
    payload = (
        {
            "air_temperature": 330,
            "process_temperature": 350,
            "rotational_speed": 1150,
            "torque": 90,
            "tool_wear": 240,
        }
        if probability_hint == "critical"
        else {
            "air_temperature": 298,
            "process_temperature": 308,
            "rotational_speed": 1500,
            "torque": 40,
            "tool_wear": 10,
        }
    )
    return client.post(f"/prediction/?machine_id={machine_id}", json=payload)


# -----------------------------
# GET /prediction/machines/{id} - must not perform inference or write rows
# -----------------------------

def test_get_prediction_with_no_history_returns_error_shape_and_creates_nothing(
    machine, db_session
):
    before = _prediction_count(db_session, machine.id)

    response = client.get(f"/prediction/machines/{machine.id}")

    assert response.status_code == 200
    assert "error" in response.json()
    assert _prediction_count(db_session, machine.id) == before


def test_get_prediction_returns_latest_stored_prediction_without_recomputing(
    machine, db_session
):
    create_response = _create_prediction(machine.id, "critical")
    assert create_response.status_code == 200
    created = create_response.json()

    count_after_create = _prediction_count(db_session, machine.id)

    first_get = client.get(f"/prediction/machines/{machine.id}")
    second_get = client.get(f"/prediction/machines/{machine.id}")

    assert first_get.status_code == 200
    assert second_get.status_code == 200

    first_data = first_get.json()
    second_data = second_get.json()

    # Same stored row both times - no new inference, no new row.
    assert first_data["probability"] == created["probability"]
    assert first_data["top_factors"] == created["top_factors"]
    assert first_data["risk_level"] == "CRITICAL"
    assert first_data == second_data

    assert _prediction_count(db_session, machine.id) == count_after_create


def test_get_prediction_low_risk_level(machine):
    create_response = _create_prediction(machine.id, "healthy")
    assert create_response.status_code == 200

    response = client.get(f"/prediction/machines/{machine.id}")
    assert response.status_code == 200
    assert response.json()["risk_level"] == "LOW"


def test_get_prediction_includes_input_snapshot_and_model_version(machine):
    """ML/MLOps audit, Near-Term #5: every prediction is independently
    reproducible/auditable without needing the (possibly since-changed)
    sensor reading it came from.
    """
    from app.ml import model_loader

    create_response = _create_prediction(machine.id, "critical")
    assert create_response.status_code == 200

    data = client.get(f"/prediction/machines/{machine.id}").json()

    assert data["input_features"] == {
        "air_temperature": 330,
        "process_temperature": 350,
        "rotational_speed": 1150,
        "torque": 90,
        "tool_wear": 240,
    }
    assert data["model_version"] == model_loader.MODEL_VERSION


# -----------------------------
# GET /recommendations/machines/{id} - same read-only contract
# -----------------------------

def test_get_recommendation_with_no_history_returns_404(machine, db_session):
    before = _prediction_count(db_session, machine.id)

    response = client.get(f"/recommendations/machines/{machine.id}")

    assert response.status_code == 404
    assert _prediction_count(db_session, machine.id) == before


def test_get_recommendation_does_not_create_a_new_prediction(machine, db_session):
    create_response = _create_prediction(machine.id, "critical")
    assert create_response.status_code == 200

    count_after_create = _prediction_count(db_session, machine.id)

    response = client.get(f"/recommendations/machines/{machine.id}")

    assert response.status_code == 200
    assert response.json()["priority"] == "CRITICAL"
    assert _prediction_count(db_session, machine.id) == count_after_create
