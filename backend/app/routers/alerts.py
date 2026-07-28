from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.alert import Alert


router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"]
)


# -----------------------------
# GET ACTIVE ALERTS / HISTORY
# -----------------------------

@router.get("/")
def get_alerts(
    status: str = None,
    db: Session = Depends(get_db)
):

    query = db.query(Alert)


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
        .all()
    )


    return alerts



# -----------------------------
# ACKNOWLEDGE ALERT
# -----------------------------

@router.patch("/{alert_id}/acknowledge")
def acknowledge_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):

    alert = (
        db.query(Alert)
        .filter(
            Alert.id == alert_id
        )
        .first()
    )


    if not alert:

        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )


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

@router.patch("/{alert_id}/resolve")
def resolve_alert(
    alert_id: int,
    db: Session = Depends(get_db)
):

    alert = (
        db.query(Alert)
        .filter(
            Alert.id == alert_id
        )
        .first()
    )


    if not alert:

        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )


    if alert.status == "RESOLVED":

        return alert


    alert.status = "RESOLVED"
    alert.resolved_at = datetime.utcnow()


    db.commit()
    db.refresh(alert)


    return alert