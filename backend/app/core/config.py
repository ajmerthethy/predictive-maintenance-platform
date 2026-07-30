import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL"
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