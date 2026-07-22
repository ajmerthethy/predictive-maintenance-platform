
import pandas as pd
from sqlalchemy.orm import Session

from app.models.sensor_reading import SensorReading


def create_sensor_features(db: Session, machine_id: int):
    """
    Extract sensor data and create ML features.
    """

    # Get sensor readings for a machine
    readings = (
        db.query(SensorReading)
        .filter(SensorReading.machine_id == machine_id)
        .order_by(SensorReading.timestamp)
        .all()
    )

    # Convert SQLAlchemy objects into dictionaries
    data = [
        {
            "temperature": reading.temperature,
            "vibration": reading.vibration,
            "pressure": reading.pressure,
            "timestamp": reading.timestamp
        }
        for reading in readings
    ]

    # Convert to dataframe
    df = pd.DataFrame(data)

    if df.empty:
        return df

    # Create rolling features
    df["temperature_avg_5"] = (
        df["temperature"].rolling(window=5).mean()
    )

    df["vibration_avg_5"] = (
        df["vibration"]
        .rolling(window=5)
        .mean()
    )

    df["pressure_avg_5"] = (
        df["pressure"]
        .rolling(window=5)
        .mean()
    )

    # Fill missing values from first few rows
    df = df.bfill()

    return df