import joblib
import pandas as pd
import os

MODEL_PATH = os.path.join(
    "app",
    "ml",
    "saved_models",
    "failure_model.pkl"
)

model = joblib.load(MODEL_PATH)


def predict_failure(
    temperature: float,
    vibration: float,
    pressure: float
):

    features = pd.DataFrame(
        [
            {
                "temperature": temperature,
                "vibration": vibration,
                "pressure": pressure
            }
        ]
    )

    prediction = model.predict(features)[0]
    probability = model.predict_proba(features)[0][1]

    return {
        "prediction": int(prediction),
        "probability": float(probability)
    }