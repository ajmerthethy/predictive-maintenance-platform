from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AlertResponse(BaseModel):
    id: int
    machine_id: int
    severity: str
    message: str
    probability: float
    recommended_action: str
    status: str
    created_at: datetime
    resolved_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )
