
# app/services/prediction_service.py

from app.ml.live_prediction import predict_failure_from_reading

def run_prediction(db, machine_id: int):

    result = predict_failure_from_reading(
        db,
        machine_id
    )

    return result