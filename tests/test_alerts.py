from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_get_alerts():

    response = client.get(
        "/alerts/"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

def test_acknowledge_alert(alert):

    response = client.patch(
        f"/alerts/{alert.id}/acknowledge"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ACKNOWLEDGED"

def test_acknowledge_alert_not_found():

    response = client.patch(
        "/alerts/999999/acknowledge"
    )

    assert response.status_code == 404

def test_resolve_alert(alert):

    response = client.patch(
        f"/alerts/{alert.id}/resolve"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "RESOLVED"

def test_resolve_alert_not_found():

    response = client.patch(
        "/alerts/999999/resolve"
    )

    assert response.status_code == 404
