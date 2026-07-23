import joblib
import pandas as pd
import os
import shap


MODEL_PATH = os.path.join(
    "app",
    "ml",
    "saved_models",
    "failure_model.pkl"
)


model = joblib.load(MODEL_PATH)

explainer = shap.TreeExplainer(model)


def predict_failure(
    air_temperature: float,
    process_temperature: float,
    rotational_speed: float,
    torque: float,
    tool_wear: float
):

    features = pd.DataFrame(
        [
            {
                "Air temperature [K]": air_temperature,
                "Process temperature [K]": process_temperature,
                "Rotational speed [rpm]": rotational_speed,
                "Torque [Nm]": torque,
                "Tool wear [min]": tool_wear
            }
        ]
    )


    prediction = model.predict(features)[0]

    probability = model.predict_proba(features)[0][1]


    shap_values = explainer(features)


    return {
        "prediction": int(prediction),
        "probability": float(probability),
        "shap_values": {
            feature: float(value)
            for feature, value in zip(
                features.columns,
                shap_values.values[0, :, 1]
            )
        }
    }