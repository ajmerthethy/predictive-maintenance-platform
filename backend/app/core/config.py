import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

# Auth. JWT_SECRET_KEY MUST be set to a real random value in any deployed
# environment (e.g. `python -c "import secrets; print(secrets.token_hex(32))"`).
# The fallback below is for local dev convenience only - using it anywhere
# real means anyone can forge valid login tokens.
JWT_SECRET_KEY = os.getenv(
    "JWT_SECRET_KEY", "insecure-dev-secret-change-me"
)

JWT_ALGORITHM = "HS256"

JWT_EXPIRATION_HOURS = int(
    os.getenv("JWT_EXPIRATION_HOURS", "24")
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