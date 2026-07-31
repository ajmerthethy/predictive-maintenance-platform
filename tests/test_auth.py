from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import JWT_ALGORITHM, JWT_SECRET_KEY, JWT_EXPIRATION_HOURS
from app.core.security import create_access_token, get_current_user, hash_password
from app.models.user import User

client = TestClient(app)


@pytest.fixture()
def real_auth():
    """Temporarily disable the session-wide auth-bypass override (see
    conftest.py's _bypass_auth) so tests in this module exercise the real
    get_current_user dependency chain end to end, not a stubbed-out user.
    """
    original_override = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides.pop(get_current_user, None)
    yield
    if original_override is not None:
        app.dependency_overrides[get_current_user] = original_override


@pytest.fixture()
def test_user(db_session, _test_account_id):
    user = User(
        username="auth_test_user",
        email="auth_test_user@example.com",
        hashed_password=hash_password("CorrectHorseBattery1!"),
        role="operator",
        account_id=_test_account_id,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def _forge_token(secret, sub="auth_test_user", expires_delta=timedelta(hours=1)):
    return jwt.encode(
        {
            "sub": sub,
            "exp": datetime.now(timezone.utc) + expires_delta,
        },
        secret,
        algorithm=JWT_ALGORITHM,
    )


# -----------------------------
# TOKEN ISSUANCE (POST /auth/login)
# -----------------------------

def test_login_success_returns_valid_token(real_auth, test_user):
    response = client.post(
        "/auth/login",
        json={"username": "auth_test_user", "password": "CorrectHorseBattery1!"},
    )

    assert response.status_code == 200

    body = response.json()
    assert body["token_type"] == "bearer"

    payload = jwt.decode(
        body["access_token"], JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM]
    )
    assert payload["sub"] == "auth_test_user"
    assert "exp" in payload


def test_login_token_expiry_matches_configured_duration(real_auth, test_user):
    response = client.post(
        "/auth/login",
        json={"username": "auth_test_user", "password": "CorrectHorseBattery1!"},
    )

    payload = jwt.decode(
        response.json()["access_token"], JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM]
    )
    expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    expected = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)

    # Small tolerance for the time elapsed running the test itself.
    assert abs((expires_at - expected).total_seconds()) < 10


def test_login_wrong_password_returns_401(real_auth, test_user):
    response = client.post(
        "/auth/login",
        json={"username": "auth_test_user", "password": "WrongPassword!"},
    )

    assert response.status_code == 401


def test_login_nonexistent_user_returns_401(real_auth):
    response = client.post(
        "/auth/login",
        json={"username": "does_not_exist", "password": "whatever"},
    )

    assert response.status_code == 401


def test_login_error_does_not_distinguish_bad_password_from_no_such_user(
    real_auth, test_user
):
    """Same detail message either way, so a caller can't use the error
    to enumerate which usernames exist.
    """

    wrong_password = client.post(
        "/auth/login",
        json={"username": "auth_test_user", "password": "WrongPassword!"},
    )
    no_such_user = client.post(
        "/auth/login",
        json={"username": "nobody_by_this_name", "password": "WrongPassword!"},
    )

    assert wrong_password.json()["detail"] == no_such_user.json()["detail"]


# -----------------------------
# TOKEN VALIDATION (general protected route, not just health.router)
# -----------------------------

def test_protected_route_without_token_returns_401(real_auth):
    response = client.get("/machines/")
    assert response.status_code in (401, 403)


def test_protected_route_with_malformed_token_returns_401(real_auth):
    response = client.get(
        "/machines/", headers={"Authorization": "Bearer not-a-real-jwt"}
    )
    assert response.status_code == 401


def test_protected_route_with_wrong_signature_returns_401(real_auth):
    forged = _forge_token(secret="a-completely-different-secret-not-the-real-one")

    response = client.get(
        "/machines/", headers={"Authorization": f"Bearer {forged}"}
    )
    assert response.status_code == 401


def test_protected_route_with_expired_token_returns_401(real_auth, test_user):
    expired = _forge_token(
        secret=JWT_SECRET_KEY,
        sub=test_user.username,
        expires_delta=timedelta(hours=-1),
    )

    response = client.get(
        "/machines/", headers={"Authorization": f"Bearer {expired}"}
    )
    assert response.status_code == 401


def test_protected_route_with_token_for_unknown_user_returns_401(real_auth):
    # Validly signed, unexpired, but the subject doesn't exist in the DB -
    # e.g. a user deleted after their token was issued.
    token = create_access_token("someone_who_does_not_exist_in_the_db")

    response = client.get(
        "/machines/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401


def test_protected_route_with_valid_token_returns_200(real_auth, test_user):
    login_response = client.post(
        "/auth/login",
        json={"username": "auth_test_user", "password": "CorrectHorseBattery1!"},
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/machines/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


# -----------------------------
# CROSS-ACCOUNT ISOLATION
# -----------------------------
# Full coverage (two real users, two accounts, list/read/write/predict
# all denied across accounts) lives in test_tenant_isolation.py - not
# duplicated here.
