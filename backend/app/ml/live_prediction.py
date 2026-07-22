import joblib
import os
import pandas as pd

from app.models.machine import Machine
from app.models.prediction import Prediction
from app.models.sensor_reading import SensorReading

MODEL_PATH = os.path.join(
    "app",
    "ml",
    "saved_models",
    "failure_model.pkl"
)

model = joblib.load(MODEL_PATH)


def predict_failure_from_reading(db, machine_id: int):

    reading = (
        db.query(SensorReading)
        .filter(SensorReading.machine_id == machine_id)
        .order_by(SensorReading.timestamp.desc())
        .first()
    )

    if reading is None:
        return {
            "error": "No sensor readings found for the specified machine."
        }

    features = pd.DataFrame(
        [
            {
                "temperature": reading.temperature,
                "vibration": reading.vibration,
                "pressure": reading.pressure
            }
        ]
    )

    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0][1]

    return {
        "machine_id": machine_id,
        "temperature": reading.temperature,
        "vibration": reading.vibration,
        "pressure": reading.pressure,
        "prediction": int(prediction),
        "probability": float(probability)
    }