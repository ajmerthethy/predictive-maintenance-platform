import logging
from types import SimpleNamespace

import pytest
import requests
from fastapi.testclient import TestClient

from app.main import app
from app.services import notifications
from app.services.alert_service import generate_alert

client = TestClient(app)


# -----------------------------
# THRESHOLD LOGIC: does an alert get generated for the right probability?
# -----------------------------

@pytest.mark.parametrize("probability", [0.0, 0.3, 0.49, 0.5, 0.7, 0.749])
def test_generate_alert_none_below_critical_threshold(probability):
    """Only CRITICAL risk (>=0.75) creates an alert - WARNING (0.50-0.74)
    and LOW do not, by current design (see app/services/risk_service.py).
    """
    prediction = SimpleNamespace(probability=probability)
    assert generate_alert(prediction) is None


@pytest.mark.parametrize("probability", [0.75, 0.8, 0.95, 1.0])
def test_generate_alert_triggers_at_and_above_critical_threshold(probability):
    prediction = SimpleNamespace(probability=probability)
    alert_data = generate_alert(prediction)

    assert alert_data is not None
    assert alert_data["severity"] == "HIGH"
    assert alert_data["message"]
    assert alert_data["recommended_action"]


def test_generate_alert_boundary_just_below_threshold():
    assert generate_alert(SimpleNamespace(probability=0.7499999)) is None


def test_generate_alert_boundary_exactly_at_threshold():
    assert generate_alert(SimpleNamespace(probability=0.75)) is not None


# -----------------------------
# DELIVERY: does send_alert_email actually attempt/skip correctly?
# -----------------------------

def _alert(probability=0.9, severity="HIGH", alert_id=1):
    return SimpleNamespace(
        id=alert_id,
        probability=probability,
        severity=severity,
        recommended_action="Inspect machine within 24 hours",
    )


def _machine(machine_id=1, name="Test Machine", location="Test Site"):
    return SimpleNamespace(id=machine_id, name=name, location=location)


class _RecordingPost:
    """Stand-in for requests.post that records calls instead of making
    a real network request, and returns whatever response/exception it
    was configured with.
    """

    def __init__(self, response=None, exception=None):
        self.response = response
        self.exception = exception
        self.calls = []

    def __call__(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if self.exception:
            raise self.exception
        return self.response


class _FakeResponse:
    def __init__(self, status_code, text=""):
        self.status_code = status_code
        self.text = text


def test_send_alert_email_skips_when_api_key_unset(monkeypatch):
    monkeypatch.setattr(notifications, "RESEND_API_KEY", None)
    monkeypatch.setattr(notifications, "EMAIL_ALERT_RECIPIENT", "someone@example.com")
    fake_post = _RecordingPost()
    monkeypatch.setattr(notifications.requests, "post", fake_post)

    notifications.send_alert_email(_alert(), _machine())

    assert fake_post.calls == []


def test_send_alert_email_skips_when_recipient_unset(monkeypatch):
    monkeypatch.setattr(notifications, "RESEND_API_KEY", "re_fake_key")
    monkeypatch.setattr(notifications, "EMAIL_ALERT_RECIPIENT", None)
    fake_post = _RecordingPost()
    monkeypatch.setattr(notifications.requests, "post", fake_post)

    notifications.send_alert_email(_alert(), _machine())

    assert fake_post.calls == []


def test_send_alert_email_sends_correct_payload_when_configured(monkeypatch):
    monkeypatch.setattr(notifications, "RESEND_API_KEY", "re_fake_key")
    monkeypatch.setattr(notifications, "EMAIL_ALERT_RECIPIENT", "customer@example.com")
    monkeypatch.setattr(notifications, "RESEND_FROM_EMAIL", "alerts@realdomain.com")
    fake_post = _RecordingPost(response=_FakeResponse(200))
    monkeypatch.setattr(notifications.requests, "post", fake_post)

    alert = _alert(probability=0.9123, severity="HIGH", alert_id=42)
    machine = _machine(name="Industrial Turbine 001", location="Power Room")

    notifications.send_alert_email(alert, machine)

    assert len(fake_post.calls) == 1
    url, kwargs = fake_post.calls[0]
    assert url == notifications.RESEND_API_URL
    assert kwargs["headers"]["Authorization"] == "Bearer re_fake_key"

    payload = kwargs["json"]
    assert payload["from"] == "alerts@realdomain.com"
    assert payload["to"] == ["customer@example.com"]
    assert "Industrial Turbine 001" in payload["subject"]
    assert "HIGH" in payload["subject"]
    assert "Industrial Turbine 001" in payload["html"]
    assert "Power Room" in payload["html"]
    assert "91.2%" in payload["html"]  # probability rounded to 1 decimal
    assert "Inspect machine within 24 hours" in payload["html"]


def test_send_alert_email_logs_error_on_http_failure_and_does_not_raise(
    monkeypatch, caplog
):
    monkeypatch.setattr(notifications, "RESEND_API_KEY", "re_fake_key")
    monkeypatch.setattr(notifications, "EMAIL_ALERT_RECIPIENT", "customer@example.com")
    monkeypatch.setattr(notifications, "RESEND_FROM_EMAIL", "alerts@realdomain.com")
    fake_post = _RecordingPost(response=_FakeResponse(500, text="internal error"))
    monkeypatch.setattr(notifications.requests, "post", fake_post)

    with caplog.at_level(logging.ERROR):
        notifications.send_alert_email(_alert(alert_id=99), _machine())

    assert any(
        "99" in record.getMessage() and "failed" in record.getMessage().lower()
        for record in caplog.records
    )


def test_send_alert_email_logs_exception_on_network_error_and_does_not_raise(
    monkeypatch, caplog
):
    monkeypatch.setattr(notifications, "RESEND_API_KEY", "re_fake_key")
    monkeypatch.setattr(notifications, "EMAIL_ALERT_RECIPIENT", "customer@example.com")
    monkeypatch.setattr(notifications, "RESEND_FROM_EMAIL", "alerts@realdomain.com")
    fake_post = _RecordingPost(
        exception=requests.exceptions.ConnectionError("network is unreachable")
    )
    monkeypatch.setattr(notifications.requests, "post", fake_post)

    with caplog.at_level(logging.ERROR):
        # Must not raise - a Resend outage can never break the prediction
        # request that triggered this.
        notifications.send_alert_email(_alert(alert_id=7), _machine())

    assert any("7" in record.getMessage() for record in caplog.records)


def test_send_alert_email_warns_when_using_sandbox_sender(monkeypatch, caplog):
    monkeypatch.setattr(notifications, "RESEND_API_KEY", "re_fake_key")
    monkeypatch.setattr(notifications, "EMAIL_ALERT_RECIPIENT", "customer@example.com")
    monkeypatch.setattr(
        notifications, "RESEND_FROM_EMAIL", notifications.RESEND_SANDBOX_SENDER
    )
    fake_post = _RecordingPost(response=_FakeResponse(200))
    monkeypatch.setattr(notifications.requests, "post", fake_post)

    with caplog.at_level(logging.ERROR):
        notifications.send_alert_email(_alert(), _machine())

    assert any("sandbox" in record.getMessage().lower() for record in caplog.records)


# -----------------------------
# END TO END: does hitting the real endpoint attempt delivery correctly?
# -----------------------------

def test_prediction_endpoint_attempts_email_on_critical_prediction(
    machine, monkeypatch
):
    monkeypatch.setattr(notifications, "RESEND_API_KEY", "re_fake_key")
    monkeypatch.setattr(notifications, "EMAIL_ALERT_RECIPIENT", "customer@example.com")
    fake_post = _RecordingPost(response=_FakeResponse(200))
    monkeypatch.setattr(notifications.requests, "post", fake_post)

    # Same extreme sensor values verified earlier to produce a
    # CRITICAL-range prediction (probability ~0.84) against the real model.
    response = client.post(
        f"/prediction/?machine_id={machine.id}",
        json={
            "air_temperature": 330,
            "process_temperature": 350,
            "rotational_speed": 1150,
            "torque": 90,
            "tool_wear": 240,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["probability"] >= 0.75
    assert data["alert_created"] is True
    assert len(fake_post.calls) == 1


def test_prediction_endpoint_does_not_email_on_healthy_prediction(
    machine, monkeypatch
):
    monkeypatch.setattr(notifications, "RESEND_API_KEY", "re_fake_key")
    monkeypatch.setattr(notifications, "EMAIL_ALERT_RECIPIENT", "customer@example.com")
    fake_post = _RecordingPost(response=_FakeResponse(200))
    monkeypatch.setattr(notifications.requests, "post", fake_post)

    response = client.post(
        f"/prediction/?machine_id={machine.id}",
        json={
            "air_temperature": 298,
            "process_temperature": 308,
            "rotational_speed": 1500,
            "torque": 40,
            "tool_wear": 10,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["alert_created"] is False
    assert fake_post.calls == []
