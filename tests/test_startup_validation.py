import logging
import os
import subprocess
import sys
from pathlib import Path

import pytest

from app.core import config
from app.core.config import (
    check_resend_sender_configured,
    validate_jwt_secret_key,
    MIN_JWT_SECRET_LENGTH,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = REPO_ROOT / "backend"


@pytest.mark.parametrize(
    "value",
    [
        None,
        "",
        "   ",
        "a" * (MIN_JWT_SECRET_LENGTH - 1),
    ],
)
def test_validate_jwt_secret_key_rejects_invalid_values(value):
    with pytest.raises(RuntimeError):
        validate_jwt_secret_key(value)


def test_validate_jwt_secret_key_accepts_valid_value():
    validate_jwt_secret_key("a" * MIN_JWT_SECRET_LENGTH)


def test_app_fails_to_import_without_jwt_secret():
    """End-to-end version of the check above: importing app.main itself
    must fail, not just the helper function in isolation.

    Sets JWT_SECRET_KEY="" explicitly rather than leaving it unset in the
    subprocess env. load_dotenv() (called at import time by
    app.core.config) discovers .env based on config.py's own file
    location, not this test's cwd, and would silently repopulate a truly
    absent key from the real .env file on disk. An explicit empty string
    survives, since load_dotenv() defaults to override=False.
    """

    env = {
        **os.environ,
        "JWT_SECRET_KEY": "",
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/placeholder",
    }

    result = subprocess.run(
        [sys.executable, "-c", "import app.main"],
        cwd=str(BACKEND_DIR),
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "JWT_SECRET_KEY" in result.stderr


def test_app_imports_successfully_with_valid_jwt_secret():
    env = {
        **os.environ,
        "JWT_SECRET_KEY": "a" * MIN_JWT_SECRET_LENGTH,
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/placeholder",
    }

    result = subprocess.run(
        [sys.executable, "-c", "import app.main"],
        cwd=str(BACKEND_DIR),
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def test_resend_sender_check_logs_error_when_still_sandbox(monkeypatch, caplog):
    monkeypatch.setattr(config, "RESEND_API_KEY", "re_fake_key_for_test")
    monkeypatch.setattr(
        config, "RESEND_FROM_EMAIL", config.RESEND_SANDBOX_SENDER
    )

    with caplog.at_level(logging.ERROR):
        check_resend_sender_configured()

    assert any(
        "sandbox sender" in record.message for record in caplog.records
    )


def test_resend_sender_check_silent_with_verified_sender(monkeypatch, caplog):
    monkeypatch.setattr(config, "RESEND_API_KEY", "re_fake_key_for_test")
    monkeypatch.setattr(config, "RESEND_FROM_EMAIL", "alerts@realcustomer.com")

    with caplog.at_level(logging.ERROR):
        check_resend_sender_configured()

    assert caplog.records == []


def test_resend_sender_check_silent_when_alerting_disabled(monkeypatch, caplog):
    monkeypatch.setattr(config, "RESEND_API_KEY", None)
    monkeypatch.setattr(
        config, "RESEND_FROM_EMAIL", config.RESEND_SANDBOX_SENDER
    )

    with caplog.at_level(logging.ERROR):
        check_resend_sender_configured()

    assert caplog.records == []
