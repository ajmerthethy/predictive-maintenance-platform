import logging

from fastapi.testclient import TestClient

from app.main import app
from app.core.security import get_current_user
from app.db.database import get_db


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy"
    }


def test_health_check_requires_no_auth():
    """Pure liveness - an external monitor won't have a bearer token."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_db_check_returns_200_when_database_reachable():
    response = client.get("/health/db")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "database": "reachable"}


def test_health_db_check_returns_503_and_logs_when_database_unreachable(caplog):
    class _BrokenSession:
        def execute(self, *args, **kwargs):
            raise RuntimeError("simulated database outage for this test")

        def close(self):
            pass

    app.dependency_overrides[get_db] = lambda: _BrokenSession()

    with caplog.at_level(logging.ERROR):
        response = client.get("/health/db")

    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}
    assert any(
        "Database health check failed" in record.getMessage()
        for record in caplog.records
    )


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