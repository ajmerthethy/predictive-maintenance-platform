from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_get_maintenance_tasks():

    response = client.get(
        "/maintenance/"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

def test_create_maintenance_task(machine):

    response = client.post(
        "/maintenance/",
        json={
            "machine_id": machine.id,
            "description": "Replace worn cutting tool",
            "technician": "John Smith"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["machine_id"] == machine.id
    assert data["description"] == "Replace worn cutting tool"
    assert data["technician"] == "John Smith"
    assert data["status"] == "OPEN"

def test_complete_maintenance_task(maintenance_task):

    response = client.patch(
        f"/maintenance/{maintenance_task.id}/complete"
    )

    assert response.status_code == 200
    assert response.json()["status"] == "COMPLETED"

def test_complete_maintenance_task_not_found():

    response = client.patch(
        "/maintenance/999999/complete"
    )

    assert response.status_code == 404