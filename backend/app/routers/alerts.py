from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.alert import Alert
from app.models.machine import Machine
from app.models.user import User
from app.schemas.alert import AlertResponse
from app.services.tenancy import get_owned_alert_or_404


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)


# -----------------------------
# GET ACTIVE ALERTS / HISTORY
# -----------------------------

@router.get("/", response_model=list[AlertResponse])
def get_alerts(
    status: str = None,
    limit: int = Query(200, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    query = (
        db.query(Alert)
        .join(Machine, Alert.machine_id == Machine.id)
        .filter(Machine.account_id == current_user.account_id)
    )


    if status:

        # Example:
        # /alerts/?status=RESOLVED

        query = query.filter(
            Alert.status == status
        )


    else:

        # Default dashboard view
        # Hide resolved alerts

        query = query.filter(
            Alert.status != "RESOLVED"
        )


    alerts = (
        query
        .order_by(
            desc(Alert.created_at)
        )
        .offset(offset)
        .limit(limit)
        .all()
    )


    return alerts



# -----------------------------
# ACKNOWLEDGE ALERT
# -----------------------------

@router.patch("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    alert = get_owned_alert_or_404(db, alert_id, current_user.account_id)


    if alert.status == "RESOLVED":

        raise HTTPException(
            status_code=400,
            detail="Resolved alert cannot be acknowledged."
        )


    alert.status = "ACKNOWLEDGED"


    db.commit()
    db.refresh(alert)


    return alert



# -----------------------------
# RESOLVE ALERT
# -----------------------------

@router.patch("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    alert = get_owned_alert_or_404(db, alert_id, current_user.account_id)


    if alert.status == "RESOLVED":

        return alert


    alert.status = "RESOLVED"
    alert.resolved_at = datetime.utcnow()


    db.commit()
    db.refresh(alert)


    return alert