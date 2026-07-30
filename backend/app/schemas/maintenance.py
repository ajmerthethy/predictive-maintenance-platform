from datetime import datetime
from pydantic import BaseModel, ConfigDict


class MaintenanceTaskResponse(BaseModel):
    id: int
    machine_id: int
    alert_id: int | None
    description: str
    technician: str | None
    status: str
    cost: float | None
    created_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(
        from_attributes=True
    )
