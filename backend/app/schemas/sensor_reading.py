from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SensorReadingCreate(BaseModel):
    machine_id: int
    air_temperature: float
    process_temperature: float
    rotational_speed: float
    torque: float
    tool_wear: float
    timestamp: datetime | None = None
    # Optional, defaults to today's implicit behavior (the column already
    # defaulted to False before this field existed). Lets a technician who
    # knows a machine actually failed record that outcome, so model
    # performance can eventually be checked against reality (see
    # app.services.model_performance) - nothing set this before, so
    # sensor_readings.failure was always False in practice.
    failure: bool = False


class SensorReadingResponse(BaseModel):
    id: int
    machine_id: int
    air_temperature: float
    process_temperature: float
    rotational_speed: float
    torque: float
    tool_wear: float
    failure: bool
    timestamp: datetime

    model_config = ConfigDict(
        from_attributes=True
    )