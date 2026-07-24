
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

def test_prediction_endpoint():

    response = client.post(
        "/prediction/?machine_id=1",
        json = {
            "air_temperature": 300.0,
            "process_temperature": 310.0,
            "rotational_speed": 1500.0,
            "torque": 40.0,
            "tool_wear": 100.0
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "prediction" in data
    assert "probability" in data
    assert "top_factors" in data
