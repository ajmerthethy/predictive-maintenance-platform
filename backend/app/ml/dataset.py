import pandas as pd

from app.models.sensor_reading import SensorReading


def create_training_dataset(db):

    readings = (
        db.query(SensorReading)
        .order_by(SensorReading.timestamp)
        .all()
    )

    data = []

    for r in readings:

        failure = (
            r.temperature > 80
            or r.vibration > 2.5
            or r.pressure < 95
        )

        data.append(
            {
                "temperature": r.temperature,
                "vibration": r.vibration,
                "pressure": r.pressure,
                "failure": int(failure)
            }
        )

    return pd.DataFrame(data)