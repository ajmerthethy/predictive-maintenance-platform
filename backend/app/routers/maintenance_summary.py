from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.machine import Machine
from app.models.maintenance import MaintenanceTask
from app.models.alert import Alert


router = APIRouter(
    prefix="/machines",
    tags=["Maintenance Summary"]
)


@router.get("/{machine_id}/maintenance-summary")
def maintenance_summary(
    machine_id: int,
    db: Session = Depends(get_db)
):

    machine = (
        db.query(Machine)
        .filter(
            Machine.id == machine_id
        )
        .first()
    )


    if not machine:
        return {
            "error": "Machine not found"
        }


    tasks = (
        db.query(MaintenanceTask)
        .filter(
            MaintenanceTask.machine_id == machine_id
        )
        .all()
    )


    alerts = (
        db.query(Alert)
        .filter(
            Alert.machine_id == machine_id
        )
        .all()
    )


    completed = len(
        [
            t for t in tasks
            if t.status == "COMPLETED"
        ]
    )


    open_tasks = len(
        [
            t for t in tasks
            if t.status == "OPEN"
        ]
    )

    in_progress_tasks = len(
        [
            t for t in tasks
            if t.status == "IN_PROGRESS"
        ]
    )


    return {

        "machine": machine.name,

        "total_work_orders": len(tasks),

        "completed_work_orders": completed,

        "open_work_orders": open_tasks,

        "in_progress_work_orders": in_progress_tasks,

        "failure_events": len(alerts)

    }