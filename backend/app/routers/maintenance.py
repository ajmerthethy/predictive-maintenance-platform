from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime

from pydantic import BaseModel

from app.db.database import get_db
from app.models.maintenance import MaintenanceTask


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

@router.post("/")
def create_task(
    task_data: MaintenanceCreate,
    db: Session = Depends(get_db)
):

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

@router.get("/")
def get_tasks(
    status: str = None,
    db: Session = Depends(get_db)
):

    query = (
        db.query(MaintenanceTask)
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
        .all()
    )


    return tasks



# -----------------------------
# START WORK ORDER
# -----------------------------

@router.patch("/{task_id}/start")
def start_task(
    task_id: int,
    db: Session = Depends(get_db)
):

    task = (
        db.query(MaintenanceTask)
        .filter(
            MaintenanceTask.id == task_id
        )
        .first()
    )


    if not task:

        raise HTTPException(
            status_code=404,
            detail="Maintenance task not found"
        )


    task.status = "IN_PROGRESS"


    db.commit()
    db.refresh(task)


    return task



# -----------------------------
# COMPLETE WORK ORDER
# -----------------------------

@router.patch("/{task_id}/complete")
def complete_task(
    task_id: int,
    db: Session = Depends(get_db)
):

    task = (
        db.query(MaintenanceTask)
        .filter(
            MaintenanceTask.id == task_id
        )
        .first()
    )


    if not task:

        raise HTTPException(
            status_code=404,
            detail="Maintenance task not found"
        )


    task.status = "COMPLETED"
    task.completed_at = datetime.utcnow()


    db.commit()
    db.refresh(task)


    return task