from fastapi import HTTPException

from app.models.alert import Alert
from app.models.machine import Machine
from app.models.maintenance import MaintenanceTask

# 404, not 403, on every ownership failure below - deliberately. Returning
# a different status for "doesn't exist" vs. "exists but isn't yours"
# lets an attacker enumerate valid IDs belonging to other accounts by
# watching which status code comes back. One account should never be able
# to tell the difference between those two cases for another account's data.

NOT_FOUND = "Not found"


def get_owned_machine_or_404(db, machine_id, account_id):
    machine = (
        db.query(Machine)
        .filter(Machine.id == machine_id, Machine.account_id == account_id)
        .first()
    )

    if not machine:
        raise HTTPException(status_code=404, detail=NOT_FOUND)

    return machine


def get_owned_alert_or_404(db, alert_id, account_id):
    alert = (
        db.query(Alert)
        .join(Machine, Alert.machine_id == Machine.id)
        .filter(Alert.id == alert_id, Machine.account_id == account_id)
        .first()
    )

    if not alert:
        raise HTTPException(status_code=404, detail=NOT_FOUND)

    return alert


def get_owned_maintenance_task_or_404(db, task_id, account_id):
    task = (
        db.query(MaintenanceTask)
        .join(Machine, MaintenanceTask.machine_id == Machine.id)
        .filter(MaintenanceTask.id == task_id, Machine.account_id == account_id)
        .first()
    )

    if not task:
        raise HTTPException(status_code=404, detail=NOT_FOUND)

    return task
