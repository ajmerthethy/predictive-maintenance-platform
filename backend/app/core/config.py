import logging
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

# Auth. No fallback value on purpose - a missing or weak secret must stop
# the app from booting rather than silently accept forgeable tokens. See
# validate_jwt_secret_key(), called from main.py at startup. Generate a
# real one with: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

MIN_JWT_SECRET_LENGTH = 32


def validate_jwt_secret_key(value):
    """Raise if `value` isn't usable as a JWT signing secret. Pure
    function (takes the value rather than reading the env itself) so it's
    trivial to unit test, and so importing this module never raises on
    its own - only main.py's explicit startup call does. That keeps
    Alembic and the CLI scripts, which only need DATABASE_URL, unaffected.
    """

    if value is None or not value.strip():
        raise RuntimeError(
            "JWT_SECRET_KEY is not set. Generate one with: "
            'python -c "import secrets; print(secrets.token_hex(32))" '
            "and set it as an environment variable before starting the app."
        )

    if len(value) < MIN_JWT_SECRET_LENGTH:
        raise RuntimeError(
            f"JWT_SECRET_KEY is only {len(value)} characters - it must be "
            f"at least {MIN_JWT_SECRET_LENGTH}. Generate a proper one with: "
            'python -c "import secrets; print(secrets.token_hex(32))"'
        )


JWT_ALGORITHM = "HS256"

JWT_EXPIRATION_HOURS = int(
    os.getenv("JWT_EXPIRATION_HOURS", "24")
)

# Email alerting (see #7). RESEND_API_KEY unset means alerting is a no-op -
# there's no separate feature flag, an empty/missing key IS "disabled".
RESEND_API_KEY = os.getenv("RESEND_API_KEY")

# Resend's own sandbox/test sender - works with zero setup, but Resend
# restricts it to only deliver to the Resend account owner's own email,
# never an arbitrary customer recipient. Real delivery requires verifying
# a sending domain in the Resend dashboard/DNS (that step happens entirely
# outside this repo) and then pointing RESEND_FROM_EMAIL at an address on
# that domain.
RESEND_SANDBOX_SENDER = "onboarding@resend.dev"

RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL", RESEND_SANDBOX_SENDER)

EMAIL_ALERT_RECIPIENT = os.getenv("EMAIL_ALERT_RECIPIENT")


def check_resend_sender_configured():
    """Log loudly - but never raise - if email alerting is enabled
    (RESEND_API_KEY is set) while RESEND_FROM_EMAIL is still the sandbox
    default. This is not itself a broken state (it works for a single
    recipient who happens to be the Resend account owner, which is the
    current pilot setup), but it silently stops working for any other
    recipient, so it needs to be visible rather than discovered only when
    an alert never arrives. Non-fatal: this is a best-effort notification
    feature, not core app security - see validate_jwt_secret_key() for
    the pattern used where a missing/weak value *should* stop the app
    from booting.
    """

    if RESEND_API_KEY and RESEND_FROM_EMAIL == RESEND_SANDBOX_SENDER:
        logging.getLogger(__name__).error(
            "Email alerting is enabled but RESEND_FROM_EMAIL is still "
            "Resend's sandbox sender (%s). Alerts will only reach the "
            "Resend account owner's own inbox, not a real customer "
            "recipient. Verify a sending domain in the Resend dashboard "
            "(outside this repo), then set RESEND_FROM_EMAIL to an "
            "address on that domain.",
            RESEND_SANDBOX_SENDER,
        )

DASHBOARD_URL = os.getenv(
    "DASHBOARD_URL", "http://localhost:8501"
)

# Business assumptions used in downtime/ROI/executive calculations.
# Overridable via env vars; defaults match the values previously hardcoded
# inline in app/services/downtime_cost.py, app/services/maintenance_roi.py,
# and app/routers/executive.py.
DOWNTIME_BASE_DAILY_COST = float(
    os.getenv("DOWNTIME_BASE_DAILY_COST", "5000")
)

DEFAULT_MAINTENANCE_COST = float(
    os.getenv("DEFAULT_MAINTENANCE_COST", "2500")
)

DEFAULT_DOWNTIME_DAYS = int(
    os.getenv("DEFAULT_DOWNTIME_DAYS", "3")
)

DOWNTIME_EXPOSURE_PER_CRITICAL_MACHINE = float(
    os.getenv("DOWNTIME_EXPOSURE_PER_CRITICAL_MACHINE", "11250")
)

POTENTIAL_SAVINGS_PER_CRITICAL_MACHINE = float(
    os.getenv("POTENTIAL_SAVINGS_PER_CRITICAL_MACHINE", "32750")
)