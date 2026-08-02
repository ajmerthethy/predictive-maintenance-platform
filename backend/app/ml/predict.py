import logging

import pandas as pd

from app.ml.model_loader import model, explainer

logger = logging.getLogger(__name__)


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

    logger.debug(
        "Prediction=%s probability=%s",
        prediction,
        probability,
    )

    shap_values = explainer(features)

    feature_impacts = {
        feature: float(value)
        for feature, value in zip(
            features.columns,
            shap_values.values[0, :, 1]
        )
    }

    top_factors = sorted(
        feature_impacts.items(),
        key=lambda x: abs(x[1]),
        reverse=True
    )


    return {
        "prediction": int(prediction),
        "probability": float(probability),
        "top_factors": [
            {
                "feature": feature,
                "impact": impact
            }
            for feature, impact in top_factors
        ]
    }