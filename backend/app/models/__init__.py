from app.models.account import Account
from app.models.machine import Machine
from app.models.sensor_reading import SensorReading
from app.models.prediction import Prediction
from app.models.alert import Alert
from app.models.maintenance import MaintenanceTask
from app.models.user import User

# Re-exported so importing this package registers every model on
# Base.metadata (required for Base.metadata.create_all / Alembic autogenerate),
# even though nothing in this module references the names directly.
__all__ = [
    "Account",
    "Machine",
    "SensorReading",
    "Prediction",
    "Alert",
    "MaintenanceTask",
    "User",
]