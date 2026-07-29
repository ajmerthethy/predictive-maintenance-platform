from fastapi import APIRouter

from app.services.maintenance_roi import (
    calculate_maintenance_roi
)


router = APIRouter(
    prefix="/roi",
    tags=["Maintenance ROI"]
)


@router.get("/machines/{machine_id}")
def maintenance_roi(machine_id:int):

    # MVP values
    # Later these come from database

    downtime_cost = 11250

    health_score = 10


    return calculate_maintenance_roi(
        downtime_cost,
        health_score
    )