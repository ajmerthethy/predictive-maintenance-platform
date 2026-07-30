from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PredictionResponse(BaseModel):
    id: int
    machine_id: int
    prediction: int
    probability: float
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
