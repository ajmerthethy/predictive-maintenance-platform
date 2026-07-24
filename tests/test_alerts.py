from fastapi.testclient import TestClient

from backend.app.main import app 

client = TestClient(app)

def test_get_alerts():

    response = client.get(
        "/alerts/"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

def test_acknowledge_alert():

    response = client.patch(
        "/alerts/1/acknowledge"
    )

    assert response.status_code in [200, 404]

def test_resolve_alert():

    response = client.patch(
        "/alerts/1/resolve"
    )

    assert response.status_code in [200, 404]

        
    
