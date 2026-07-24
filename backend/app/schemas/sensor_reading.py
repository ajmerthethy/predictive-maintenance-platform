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