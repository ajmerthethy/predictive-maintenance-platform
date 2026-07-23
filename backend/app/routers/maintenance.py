
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc 

from app.db.database import get_db
from app.models.maintenance import MaintenanceTask 
from datetime import datetime

router = APIRouter(
    prefix="/maintenance",
    tags=["Maintenance"]
)

@router.post("/")
def create_task(
    machine_id: int,
    description: str,
    technician: str = None,
    alert_id: int = None,
    db: Session = Depends(get_db)
):
    task = MaintenanceTask(
        machine_id=machine_id,
        alert_id=alert_id,
        description=description,
        technician=technician
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task

@router.get("/")
def get_tasks(
    db: Session = Depends(get_db)

):
    tasks = (
        db.query(MaintenanceTask)
        .order_by(
            desc(MaintenanceTask.created_at)
        )
        .all()
    )

    return tasks

@router.patch("/{task_id}/complete")
def complete_task(
    task_id: int,
    db: Session = Depends(get_db)
):
    task = (
        db.query(MaintenanceTask)
        .filter(MaintenanceTask.id == task_id)
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