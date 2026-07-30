
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.machine import Machine
from app.schemas.machine import MachineCreate, MachineResponse

router = APIRouter(
    prefix="/machines",
    tags=["machines"],
)


@router.post("/", response_model=MachineResponse)
def create_machine(machine: MachineCreate, db: Session = Depends(get_db)):
    db_machine = Machine(
        name=machine.name,
        location=machine.location,
        manufacturer=machine.manufacturer,
        install_date=machine.install_date,
        status=machine.status,
    )
    db.add(db_machine)
    db.commit()
    db.refresh(db_machine)
    return db_machine

@router.get("/", response_model=list[MachineResponse])
def get_machines(
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):

    machines = (
        db.query(Machine)
        .order_by(Machine.id)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return machines