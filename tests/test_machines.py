
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

def test_create_machine():

    response = client.post(
        "/machines/",
        json = {
            "name": "CNC Machine 001",
            "location": "Factory A",
            "manufacturer": "Siemens",
            "install_date": "2025-01-01",
            "status": "active"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "CNC Machine 001"
    assert data["location"] == "Factory A"
    assert data["manufacturer"] == "Siemens"

def test_get_machines():

    response = client.get("/machines/")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)