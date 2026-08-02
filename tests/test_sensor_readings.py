from fastapi.testclient import TestClient

from app.main import app
from app.models.prediction import Prediction

client = TestClient(app)

def test_create_sensor_reading(machine):

    response = client.post(
        "/sensor_readings/",
        json={
            "machine_id": machine.id,
            "air_temperature": 300.5,
            "process_temperature": 310.5,
            "rotational_speed": 1500,
            "torque": 40,
            "tool_wear": 100,
            "timestamp": "2026-07-24T12:00:00"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["air_temperature"] == 300.5
    assert data["process_temperature"] == 310.5
    assert data["rotational_speed"] == 1500
    assert data["torque"] == 40
    assert data["tool_wear"] == 100

def test_get_sensor_readings(machine):

    response = client.get(
        f"/sensor_readings/{machine.id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_create_sensor_reading_defaults_failure_to_false(machine):
    response = client.post(
        "/sensor_readings/",
        json={
            "machine_id": machine.id,
            "air_temperature": 300.5,
            "process_temperature": 310.5,
            "rotational_speed": 1500,
            "torque": 40,
            "tool_wear": 100,
            "timestamp": "2026-07-24T12:00:00",
        },
    )
    assert response.status_code == 200
    assert response.json()["failure"] is False


def test_create_sensor_reading_records_a_confirmed_failure(machine):
    """A technician who knows the machine actually failed can record it -
    ground truth for app.services.model_performance (ML/MLOps audit,
    Near-Term #6). Nothing could set this before.
    """
    response = client.post(
        "/sensor_readings/",
        json={
            "machine_id": machine.id,
            "air_temperature": 300.5,
            "process_temperature": 310.5,
            "rotational_speed": 1500,
            "torque": 40,
            "tool_wear": 100,
            "timestamp": "2026-07-24T12:00:00",
            "failure": True,
        },
    )
    assert response.status_code == 200
    assert response.json()["failure"] is True


def _bulk_csv(machine_id):
    header = "machine_id,timestamp,air_temperature,process_temperature,rotational_speed,torque,tool_wear\n"
    rows = (
        f"{machine_id},2026-01-01 00:00:00,300.0,310.0,1500,40,100\n"
        f"{machine_id},2026-01-01 01:00:00,301.0,311.0,1510,41,101\n"
    )
    return (header + rows).encode()


def test_bulk_upload_triggers_a_prediction(machine, db_session):
    """The primary onboarding flow (CSV upload) must produce a prediction
    without a separate manual step - see ML/MLOps audit, Immediate #1.
    """

    before_count = (
        db_session.query(Prediction)
        .filter(Prediction.machine_id == machine.id)
        .count()
    )

    response = client.post(
        "/sensor_readings/bulk",
        params={"machine_id": machine.id},
        files={"file": ("readings.csv", _bulk_csv(machine.id), "text/csv")},
    )

    assert response.status_code == 200
    data = response.json()

    assert data["rows_inserted"] == 2
    assert data["prediction"] is not None
    assert "probability" in data["prediction"]
    assert "risk_level" in data["prediction"]

    after_count = (
        db_session.query(Prediction)
        .filter(Prediction.machine_id == machine.id)
        .count()
    )
    assert after_count == before_count + 1


def test_bulk_upload_without_failure_column_defaults_to_false(machine):
    """Every CSV that existed before this feature (no `failure` column at
    all) must keep working exactly as before.
    """
    response = client.post(
        "/sensor_readings/bulk",
        params={"machine_id": machine.id},
        files={"file": ("readings.csv", _bulk_csv(machine.id), "text/csv")},
    )
    assert response.status_code == 200

    readings = client.get(f"/sensor_readings/{machine.id}").json()
    assert all(reading["failure"] is False for reading in readings)


def test_bulk_upload_accepts_an_optional_failure_column(machine):
    header = (
        "machine_id,timestamp,air_temperature,process_temperature,"
        "rotational_speed,torque,tool_wear,failure\n"
    )
    rows = (
        f"{machine.id},2026-01-01 00:00:00,300.0,310.0,1500,40,100,0\n"
        f"{machine.id},2026-01-01 01:00:00,301.0,311.0,1510,41,101,1\n"
        # Leniently defaults to False rather than rejecting the row.
        f"{machine.id},2026-01-01 02:00:00,302.0,312.0,1520,42,102,not-a-bool\n"
    )
    csv_bytes = (header + rows).encode()

    response = client.post(
        "/sensor_readings/bulk",
        params={"machine_id": machine.id},
        files={"file": ("readings.csv", csv_bytes, "text/csv")},
    )

    assert response.status_code == 200
    assert response.json()["rows_inserted"] == 3

    readings = sorted(
        client.get(f"/sensor_readings/{machine.id}").json(),
        key=lambda r: r["timestamp"],
    )
    assert [r["failure"] for r in readings] == [False, True, False]