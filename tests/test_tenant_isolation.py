import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import get_current_user, hash_password
from app.models.account import Account
from app.models.user import User

client = TestClient(app)


@pytest.fixture()
def two_users(db_session):
    account_a = Account(name="Tenant Test Account A")
    account_b = Account(name="Tenant Test Account B")
    db_session.add_all([account_a, account_b])
    db_session.commit()
    db_session.refresh(account_a)
    db_session.refresh(account_b)

    user_a = User(
        username="tenant_test_user_a",
        email="tenant_test_user_a@example.com",
        hashed_password=hash_password("PasswordA123!"),
        role="operator",
        account_id=account_a.id,
    )
    user_b = User(
        username="tenant_test_user_b",
        email="tenant_test_user_b@example.com",
        hashed_password=hash_password("PasswordB123!"),
        role="operator",
        account_id=account_b.id,
    )
    db_session.add_all([user_a, user_b])
    db_session.commit()
    return user_a, user_b


def _login(username, password):
    response = client.post(
        "/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def test_user_b_cannot_access_or_modify_user_a_resources(two_users):
    """Two real users in two separate accounts, two real logins (auth
    bypass fixture disabled for this test), one machine created under
    User A's account. Every assertion below was failing before
    account-scoping was added to every router (see services/tenancy.py
    and the account_id column on Machine/User) - this was previously an
    xfail test documenting the gap; it now asserts the fix holds.
    """

    original_override = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides.pop(get_current_user, None)

    try:
        token_a = _login("tenant_test_user_a", "PasswordA123!")
        token_b = _login("tenant_test_user_b", "PasswordB123!")

        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # --- User A creates a machine and a sensor reading for it ---
        create_response = client.post(
            "/machines/",
            json={
                "name": "User A Private Machine",
                "location": "User A's Site",
            },
            headers=headers_a,
        )
        assert create_response.status_code == 200
        machine_id = create_response.json()["id"]

        reading_response = client.post(
            "/sensor_readings/",
            json={
                "machine_id": machine_id,
                "air_temperature": 300.0,
                "process_temperature": 310.0,
                "rotational_speed": 1500,
                "torque": 40,
                "tool_wear": 10,
            },
            headers=headers_a,
        )
        assert reading_response.status_code == 200

        # --- User B should not see User A's machine in a fleet list ---
        list_response = client.get("/machines/", headers=headers_b)
        assert list_response.status_code == 200
        listed_ids = [m["id"] for m in list_response.json()]
        assert machine_id not in listed_ids, (
            "User B can see User A's machine in GET /machines/"
        )

        # --- User B should not be able to read User A's sensor data by ID ---
        read_response = client.get(
            f"/sensor_readings/{machine_id}", headers=headers_b
        )
        assert read_response.status_code in (403, 404), (
            "User B can read User A's sensor readings by guessing the "
            f"machine_id (got {read_response.status_code} with real data: "
            f"{read_response.json()})"
        )

        # --- User B should not be able to write against User A's machine ---
        forged_write = client.post(
            "/sensor_readings/",
            json={
                "machine_id": machine_id,
                "air_temperature": 999.0,
                "process_temperature": 999.0,
                "rotational_speed": 1,
                "torque": 1,
                "tool_wear": 1,
            },
            headers=headers_b,
        )
        assert forged_write.status_code in (403, 404), (
            "User B can write sensor readings against User A's machine_id"
        )

        # --- User B should not be able to trigger a prediction against it ---
        forged_prediction = client.post(
            f"/prediction/?machine_id={machine_id}",
            json={
                "air_temperature": 300.0,
                "process_temperature": 310.0,
                "rotational_speed": 1500,
                "torque": 40,
                "tool_wear": 10,
            },
            headers=headers_b,
        )
        assert forged_prediction.status_code in (403, 404), (
            "User B can run a prediction against User A's machine_id"
        )

    finally:
        if original_override is not None:
            app.dependency_overrides[get_current_user] = original_override
