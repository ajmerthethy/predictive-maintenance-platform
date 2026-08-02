
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_prediction_endpoint(machine):

    response = client.post(
        f"/prediction/?machine_id={machine.id}",
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
    assert "risk_level" in data
    assert "model_version" in data


def test_explanation_endpoint_includes_feature_importance_and_model_info():
    response = client.get("/prediction/explanation")

    assert response.status_code == 200
    data = response.json()

    assert len(data["feature_importance"]) == 5

    model_info = data["model_info"]
    assert model_info["version"]
    assert model_info["algorithm"] == "RandomForestClassifier"
