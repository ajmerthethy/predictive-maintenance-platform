from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_analytics_summary():

    response = client.get(
        "/analytics/summary"
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_predictions" in data
    assert "failures_detected" in data
    assert "average_failure_probability" in data
    assert "high_risk_predictions" in data

def test_machine_risk_ranking():

    response = client.get(
        "/analytics/machines/risk"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)