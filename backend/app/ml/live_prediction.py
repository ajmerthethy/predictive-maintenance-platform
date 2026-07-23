import joblib
import os
import pandas as pd

from app.models.sensor_reading import SensorReading
from app.models.prediction import Prediction


from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "saved_models" / "failure_model.pkl"

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
                "Air temperature [K]": reading.air_temperature,
                "Process temperature [K]": reading.process_temperature,
                "Rotational speed [rpm]": reading.rotational_speed,
                "Torque [Nm]": reading.torque,
                "Tool wear [min]": reading.tool_wear
            }
        ]
    )


    prediction_value = model.predict(features)[0]

    probability = model.predict_proba(features)[0][1]


    prediction_record = Prediction(
        machine_id=machine_id,
        prediction=int(prediction_value),
        probability=float(probability)
    )


    db.add(prediction_record)
    db.commit()
    db.refresh(prediction_record)


    return {
        "machine_id": machine_id,
        "sensor_reading_id": reading.id,
        "prediction_id": prediction_record.id,
        "prediction": int(prediction_value),
        "probability": float(probability)
    }