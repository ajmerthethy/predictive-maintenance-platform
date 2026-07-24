from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

def test_get_maintenance_tasks():

    response = client.get(
        "/maintenance/"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

def test_create_maintenance_task():

    response = client.post(
        "/maintenance/",
        params={
            "machine_id":1,
            "description": "Replace worn cutting tool",
            "technician": "John Smith"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["machine_id"] == 1
    assert data["description"] == "Replace worn cutting tool"
    assert data["technician"] == "John Smith"
    assert data["status"] == "OPEN"

def test_complete_maintenance_task():

    response = client.patch(
        "/maintenance/1/complete"
    )

    assert response.status_code in [200, 404]