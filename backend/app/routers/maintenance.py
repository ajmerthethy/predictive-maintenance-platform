from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime

from pydantic import BaseModel

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.machine import Machine
from app.models.maintenance import MaintenanceTask
from app.models.user import User
from app.schemas.maintenance import MaintenanceTaskResponse
from app.services.tenancy import (
    get_owned_alert_or_404,
    get_owned_machine_or_404,
    get_owned_maintenance_task_or_404,
)


router = APIRouter(
    prefix="/maintenance",
    tags=["Maintenance"]
)


# -----------------------------
# REQUEST SCHEMA
# -----------------------------

class MaintenanceCreate(BaseModel):

    machine_id: int
    description: str
    technician: str | None = None
    alert_id: int | None = None



# -----------------------------
# CREATE WORK ORDER
# -----------------------------

@router.post("/", response_model=MaintenanceTaskResponse)
def create_task(
    task_data: MaintenanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    get_owned_machine_or_404(db, task_data.machine_id, current_user.account_id)

    if task_data.alert_id is not None:
        get_owned_alert_or_404(db, task_data.alert_id, current_user.account_id)

    task = MaintenanceTask(
        machine_id=task_data.machine_id,
        alert_id=task_data.alert_id,
        description=task_data.description,
        technician=task_data.technician,
        status="OPEN"
    )


    db.add(task)
    db.commit()
    db.refresh(task)


    return task



# -----------------------------
# GET ALL WORK ORDERS
# -----------------------------

@router.get("/", response_model=list[MaintenanceTaskResponse])
def get_tasks(
    status: str = None,
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    query = (
        db.query(MaintenanceTask)
        .join(Machine, MaintenanceTask.machine_id == Machine.id)
        .filter(Machine.account_id == current_user.account_id)
    )


    if status:

        query = query.filter(
            MaintenanceTask.status == status
        )


    tasks = (
        query
        .order_by(
            desc(
                MaintenanceTask.created_at
            )
        )
        .offset(offset)
        .limit(limit)
        .all()
    )


    return tasks



# -----------------------------
# START WORK ORDER
# -----------------------------

@router.patch("/{task_id}/start", response_model=MaintenanceTaskResponse)
def start_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    task = get_owned_maintenance_task_or_404(db, task_id, current_user.account_id)

    task.status = "IN_PROGRESS"


    db.commit()
    db.refresh(task)


    return task



# -----------------------------
# COMPLETE WORK ORDER
# -----------------------------

@router.patch("/{task_id}/complete", response_model=MaintenanceTaskResponse)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    task = get_owned_maintenance_task_or_404(db, task_id, current_user.account_id)

    task.status = "COMPLETED"
    task.completed_at = datetime.utcnow()


    db.commit()
    db.refresh(task)


    return task