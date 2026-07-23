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

    shap_values = explainer(features)

    print(type(shap_values))
    print(shap_values.values.shape)
    print(shap_values.base_values.shape)

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