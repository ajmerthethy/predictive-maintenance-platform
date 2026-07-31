import logging

import requests

from app.core.config import (
    RESEND_API_KEY,
    EMAIL_FROM_ADDRESS,
    EMAIL_ALERT_RECIPIENT,
    DASHBOARD_URL,
)

logger = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"


def send_alert_email(alert, machine):
    """Best-effort notification for a newly-created alert. Never raises -
    an email provider outage must not break the prediction request that
    triggered it (see #7 acceptance criteria). Silently skips if email
    alerting isn't configured (RESEND_API_KEY/EMAIL_ALERT_RECIPIENT unset).
    """

    if not RESEND_API_KEY or not EMAIL_ALERT_RECIPIENT:
        return

    probability_pct = round(alert.probability * 100, 1)

    subject = f"[{alert.severity}] {machine.name} - failure risk detected"

    body = f"""\
<h2>{machine.name}</h2>
<p><strong>Location:</strong> {machine.location}</p>
<p><strong>Severity:</strong> {alert.severity}</p>
<p><strong>Failure probability:</strong> {probability_pct}%</p>
<p><strong>Recommended action:</strong> {alert.recommended_action}</p>
<p><a href="{DASHBOARD_URL}">View in dashboard</a></p>
"""

    try:
        response = requests.post(
            RESEND_API_URL,
            headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
            json={
                "from": EMAIL_FROM_ADDRESS,
                "to": [EMAIL_ALERT_RECIPIENT],
                "subject": subject,
                "html": body,
            },
            timeout=10,
        )

        if response.status_code >= 400:
            logger.error(
                "Alert email failed: status=%s body=%s alert_id=%s",
                response.status_code,
                response.text,
                alert.id,
            )
        else:
            logger.info(
                "Alert email sent alert_id=%s machine_id=%s",
                alert.id,
                machine.id,
            )

    except requests.exceptions.RequestException:
        logger.exception(
            "Alert email failed to send alert_id=%s machine_id=%s",
            alert.id,
            machine.id,
        )
