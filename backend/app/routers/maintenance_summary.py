from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.maintenance import MaintenanceTask
from app.models.alert import Alert
from app.models.user import User
from app.services.tenancy import get_owned_machine_or_404


router = APIRouter(
    prefix="/machines",
    tags=["Maintenance Summary"]
)


@router.get("/{machine_id}/maintenance-summary")
def maintenance_summary(
    machine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    machine = get_owned_machine_or_404(db, machine_id, current_user.account_id)

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