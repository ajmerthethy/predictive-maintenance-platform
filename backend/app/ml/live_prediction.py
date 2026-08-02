from app.models.sensor_reading import SensorReading
from app.models.prediction import Prediction
from app.ml import model_loader
from app.ml.predict import predict_failure
from app.services.risk_service import calculate_risk_level


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
        probability=float(probability),
        sensor_reading_id=reading.id,
        top_factors=result["top_factors"],
        input_features={
            "air_temperature": reading.air_temperature,
            "process_temperature": reading.process_temperature,
            "rotational_speed": reading.rotational_speed,
            "torque": reading.torque,
            "tool_wear": reading.tool_wear,
        },
        model_version=model_loader.MODEL_VERSION,
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
        "risk_level": calculate_risk_level(probability),
        "top_factors": result["top_factors"],
        "model_version": prediction_record.model_version,
    }