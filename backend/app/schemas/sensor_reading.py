from datetime import datetime
from pydantic import BaseModel


class SensorReadingCreate(BaseModel):
    machine_id: int
    temperature: float
    vibration: float
    pressure: float
    timestamp: datetime | None = None

class SensorReadingResponse(BaseModel):
    id: int
    machine_id: int
    temperature: float
    vibration: float
    pressure: float
    timestamp: datetime

    class Config:
        from_attributes = True