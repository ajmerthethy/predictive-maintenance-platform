
from datetime import date
from pydantic import BaseModel

class MachineCreate(BaseModel):
    name: str
    location: str
    manufacturer: str | None = None
    install_date: date | None = None
    status: str | None = "Healthy"

class MachineResponse(BaseModel):
    id: int
    name: str
    location: str
    manufacturer: str | None
    install_date: date | None
    status: str

    class Config:
        from_attributes = True