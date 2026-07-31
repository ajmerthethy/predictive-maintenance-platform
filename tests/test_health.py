from fastapi.testclient import TestClient

from app.main import app
from app.core.security import get_current_user


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }


def _reading_payload(machine_id):
    return {
        "machine_id": machine_id,
        "air_temperature": 300.5,
        "process_temperature": 310.5,
        "rotational_speed": 1500,
        "torque": 40,
        "tool_wear": 100,
        "timestamp": "2026-07-24T12:00:00"
    }


def test_machine_health_requires_auth(machine):
    """GET /machines/{id}/health lives in health.router, which was
    previously registered without the auth dependency (see the
    production-refactor commit fixing this). Regression test for that:
    with the session-wide auth bypass fixture temporarily removed, this
    must behave exactly like every other protected route.
    """

    original_override = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides.pop(get_current_user, None)

    try:
        response = client.get(f"/machines/{machine.id}/health")
        assert response.status_code in (401, 403)

    finally:
        if original_override is not None:
            app.dependency_overrides[get_current_user] = original_override


def test_machine_trend_requires_auth(machine):
    """Same regression test as test_machine_health_requires_auth, for the
    sibling GET /machines/{id}/trend endpoint on the same router.
    """

    original_override = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides.pop(get_current_user, None)

    try:
        response = client.get(f"/machines/{machine.id}/trend")
        assert response.status_code in (401, 403)

    finally:
        if original_override is not None:
            app.dependency_overrides[get_current_user] = original_override


def test_machine_health_with_valid_auth_returns_200(machine):
    client.post("/sensor_readings/", json=_reading_payload(machine.id))

    response = client.get(f"/machines/{machine.id}/health")

    assert response.status_code == 200
    assert response.json()["machine_id"] == machine.id


def test_machine_trend_with_valid_auth_returns_200(machine):
    client.post("/sensor_readings/", json=_reading_payload(machine.id))

    response = client.get(f"/machines/{machine.id}/trend")

    assert response.status_code == 200
    assert response.json()["machine_id"] == machine.id