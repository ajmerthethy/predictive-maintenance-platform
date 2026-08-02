from fastapi.testclient import TestClient

from app.main import app
from app.services.sensor_validation import out_of_range_fields, violation_messages

client = TestClient(app)


VALID_READING = {
    "air_temperature": 300.0,
    "process_temperature": 310.0,
    "rotational_speed": 1500,
    "torque": 40,
    "tool_wear": 100,
}


# -----------------------------
# UNIT: out_of_range_fields()
# -----------------------------

def test_out_of_range_fields_empty_for_valid_reading():
    assert out_of_range_fields(**VALID_READING) == []


def test_out_of_range_fields_flags_negative_air_temperature():
    violations = out_of_range_fields(**{**VALID_READING, "air_temperature": -40.0})
    assert [v[0] for v in violations] == ["air_temperature"]


def test_out_of_range_fields_flags_multiple_fields():
    violations = out_of_range_fields(
        **{**VALID_READING, "torque": -5.0, "tool_wear": 999999.0}
    )
    assert {v[0] for v in violations} == {"torque", "tool_wear"}


def test_out_of_range_fields_accepts_existing_test_fixture_values():
    """These exact values are used elsewhere (test_alert_delivery.py) to
    force a CRITICAL-range prediction from the real model - the range
    bounds must stay generous enough to include them.
    """
    violations = out_of_range_fields(
        air_temperature=330,
        process_temperature=350,
        rotational_speed=1150,
        torque=90,
        tool_wear=240,
    )
    assert violations == []


def test_violation_messages_mentions_field_and_bounds():
    violations = out_of_range_fields(**{**VALID_READING, "rotational_speed": -1.0})
    messages = violation_messages(violations)
    assert len(messages) == 1
    assert "rotational_speed" in messages[0]
    assert "-1.0" in messages[0] or "-1" in messages[0]


# -----------------------------
# POST /sensor_readings/ - single reading
# -----------------------------

def test_create_sensor_reading_rejects_out_of_range_value(machine):
    response = client.post(
        "/sensor_readings/",
        json={
            "machine_id": machine.id,
            **{**VALID_READING, "air_temperature": -40.0},
            "timestamp": "2026-07-24T12:00:00",
        },
    )
    assert response.status_code == 422
    assert "air_temperature" in str(response.json()["detail"])


def test_create_sensor_reading_accepts_boundary_values(machine):
    response = client.post(
        "/sensor_readings/",
        json={
            "machine_id": machine.id,
            "air_temperature": 250.0,
            "process_temperature": 500.0,
            "rotational_speed": 10000.0,
            "torque": 1000.0,
            "tool_wear": 0.0,
            "timestamp": "2026-07-24T12:00:00",
        },
    )
    assert response.status_code == 200


# -----------------------------
# POST /prediction/ - direct prediction request
# -----------------------------

def test_prediction_endpoint_rejects_out_of_range_value(machine):
    response = client.post(
        f"/prediction/?machine_id={machine.id}",
        json={**VALID_READING, "torque": -5.0},
    )
    assert response.status_code == 422
    assert "torque" in str(response.json()["detail"])


# -----------------------------
# POST /sensor_readings/bulk - CSV upload
# -----------------------------

def _csv_bytes(rows):
    header = "machine_id,timestamp,air_temperature,process_temperature,rotational_speed,torque,tool_wear\n"
    body = "\n".join(",".join(str(v) for v in row) for row in rows)
    return (header + body + "\n").encode()


def test_bulk_upload_rejects_out_of_range_row(machine):
    csv_bytes = _csv_bytes(
        [
            (machine.id, "2026-01-01 00:00:00", 300.0, 310.0, 1500, 40, 100),
            # rotational_speed way outside [0, 10000]
            (machine.id, "2026-01-01 01:00:00", 300.0, 310.0, 999999, 40, 100),
        ]
    )

    response = client.post(
        "/sensor_readings/bulk",
        params={"machine_id": machine.id},
        files={"file": ("readings.csv", csv_bytes, "text/csv")},
    )

    assert response.status_code == 400
    detail = response.json()["detail"]
    assert any("rotational_speed" in err for err in detail["errors"])


def test_bulk_upload_accepts_realistic_rows(machine):
    csv_bytes = _csv_bytes(
        [
            (machine.id, "2026-01-01 00:00:00", 300.0, 310.0, 1500, 40, 100),
            (machine.id, "2026-01-01 01:00:00", 301.0, 311.0, 1510, 41, 101),
        ]
    )

    response = client.post(
        "/sensor_readings/bulk",
        params={"machine_id": machine.id},
        files={"file": ("readings.csv", csv_bytes, "text/csv")},
    )

    assert response.status_code == 200
    assert response.json()["rows_inserted"] == 2
