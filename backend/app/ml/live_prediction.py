import joblib

from app.models.sensor_reading import SensorReading
from app.models.prediction import Prediction
from app.ml.predict import predict_failure


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


    result = predict_failure(
        air_temperature=reading.air_temperature,
        process_temperature=reading.process_temperature,
        rotational_speed=reading.rotational_speed,
        torque=reading.torque,
        tool_wear=reading.tool_wear
    )

    prediction_value = result["prediction"]
    probability = result["probability"]


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
        "prediction": prediction_value,
        "probability": probability,
        "top_factors": result["top_factors"]
    }