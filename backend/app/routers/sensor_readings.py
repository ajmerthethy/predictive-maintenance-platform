import io
import logging

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.sensor_reading import SensorReading
from app.models.user import User
from app.schemas.sensor_reading import (
    SensorReadingCreate,
    SensorReadingResponse
)

from app.services.prediction_service import run_prediction
from app.services.tenancy import get_owned_machine_or_404

logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/sensor_readings",
    tags=["sensor_readings"]
)

BULK_UPLOAD_COLUMNS = [
    "machine_id",
    "timestamp",
    "air_temperature",
    "process_temperature",
    "rotational_speed",
    "torque",
    "tool_wear",
]

NUMERIC_COLUMNS = [
    "air_temperature",
    "process_temperature",
    "rotational_speed",
    "torque",
    "tool_wear",
]


@router.post("/", response_model=SensorReadingResponse)
def create_sensor_reading(
    reading: SensorReadingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    get_owned_machine_or_404(db, reading.machine_id, current_user.account_id)

    db_sensor_reading = SensorReading(
        machine_id=reading.machine_id,
        timestamp=reading.timestamp,
        air_temperature=reading.air_temperature,
        process_temperature=reading.process_temperature,
        rotational_speed=reading.rotational_speed,
        torque=reading.torque,
        tool_wear=reading.tool_wear
    )

    db.add(db_sensor_reading)
    db.commit()
    db.refresh(db_sensor_reading)


    # Automatically run prediction
    prediction = run_prediction(
        db,
        db_sensor_reading.machine_id
    )


    logger.info(
        "Automatic prediction for machine_id=%s: %s",
        db_sensor_reading.machine_id,
        prediction,
    )


    return db_sensor_reading



@router.get("/{machine_id}", response_model=list[SensorReadingResponse])
def get_sensor_readings(
    machine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    get_owned_machine_or_404(db, machine_id, current_user.account_id)

    readings = (
        db.query(SensorReading)
        .filter(SensorReading.machine_id == machine_id)
        .all()
    )

    return readings


@router.get("/bulk/template")
def download_bulk_upload_template():

    template_csv = (
        ",".join(BULK_UPLOAD_COLUMNS)
        + "\n"
        + "1,2026-01-15 08:00:00,298.5,309.2,1520,42.1,15\n"
    )

    return Response(
        content=template_csv,
        media_type="text/csv",
        headers={
            "Content-Disposition":
                "attachment; filename=sensor_readings_template.csv"
        },
    )


@router.post("/bulk")
def bulk_upload_sensor_readings(
    machine_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    get_owned_machine_or_404(db, machine_id, current_user.account_id)

    contents = file.file.read()

    try:
        df = pd.read_csv(io.BytesIO(contents))
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not parse file as CSV: {exc}",
        )

    missing_columns = [
        column
        for column in BULK_UPLOAD_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise HTTPException(
            status_code=400,
            detail=(
                "CSV is missing required column(s): "
                f"{', '.join(missing_columns)}"
            ),
        )

    if len(df) == 0:
        raise HTTPException(
            status_code=400,
            detail="CSV contains no rows",
        )

    # Coerce per-column rather than checking each row's raw value - a
    # single bad cell (e.g. "not-a-number") makes pandas infer the whole
    # column as strings, so even genuinely valid numbers in other rows
    # would otherwise fail an isinstance/type check.
    parsed_timestamps = pd.to_datetime(df["timestamp"], errors="coerce")
    parsed_machine_ids = pd.to_numeric(df["machine_id"], errors="coerce")
    parsed_numeric_columns = {
        column: pd.to_numeric(df[column], errors="coerce")
        for column in NUMERIC_COLUMNS
    }

    row_errors = []

    for position in range(len(df)):

        row_number = position + 2  # 1-indexed, plus the header row

        row_machine_id = parsed_machine_ids.iloc[position]

        if pd.isna(row_machine_id) or int(row_machine_id) != machine_id:
            row_errors.append(
                f"row {row_number}: machine_id "
                f"'{df['machine_id'].iloc[position]}' does not match "
                f"the selected machine ({machine_id})"
            )
            continue

        if pd.isna(parsed_timestamps.iloc[position]):
            row_errors.append(
                f"row {row_number}: invalid or missing timestamp "
                f"'{df['timestamp'].iloc[position]}'"
            )
            continue

        for column in NUMERIC_COLUMNS:

            if pd.isna(parsed_numeric_columns[column].iloc[position]):
                row_errors.append(
                    f"row {row_number}: invalid value for "
                    f"'{column}': '{df[column].iloc[position]}'"
                )

    if row_errors:
        raise HTTPException(
            status_code=400,
            detail={
                "message": (
                    f"{len(row_errors)} row(s) failed validation - "
                    "no rows were inserted"
                ),
                "errors": row_errors[:50],
            },
        )

    readings = [
        SensorReading(
            machine_id=machine_id,
            timestamp=parsed_timestamps.iloc[position].to_pydatetime(),
            air_temperature=float(parsed_numeric_columns["air_temperature"].iloc[position]),
            process_temperature=float(parsed_numeric_columns["process_temperature"].iloc[position]),
            rotational_speed=float(parsed_numeric_columns["rotational_speed"].iloc[position]),
            torque=float(parsed_numeric_columns["torque"].iloc[position]),
            tool_wear=float(parsed_numeric_columns["tool_wear"].iloc[position]),
        )
        for position in range(len(df))
    ]

    db.add_all(readings)
    db.commit()

    logger.info(
        "Bulk sensor reading upload machine_id=%s rows=%s",
        machine_id,
        len(readings),
    )

    return {
        "machine_id": machine_id,
        "rows_inserted": len(readings),
    }