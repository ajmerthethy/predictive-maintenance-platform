from fastapi.testclient import TestClient

from app.main import app

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