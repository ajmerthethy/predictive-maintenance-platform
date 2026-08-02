"""Golden-input regression tests against whatever model is currently
active (see app.ml.model_loader). These catch what the existing API-shape
tests can't: a retrain (or a change to predict.py) that silently shifts the
model's actual behavior. If one of these starts failing after a retrain,
that's either an intentional, reviewed change (update the expectation) or
exactly the regression this file exists to catch.

ML/MLOps audit, Near-Term #4.
"""

from app.ml import model_loader
from app.ml.predict import predict_failure

# Same vectors already relied on elsewhere in the suite
# (test_alert_delivery.py) to reliably land in a given risk band against
# the real model.
HEALTHY_INPUT = {
    "air_temperature": 298,
    "process_temperature": 308,
    "rotational_speed": 1500,
    "torque": 40,
    "tool_wear": 10,
}

CRITICAL_INPUT = {
    "air_temperature": 330,
    "process_temperature": 350,
    "rotational_speed": 1150,
    "torque": 90,
    "tool_wear": 240,
}


def test_healthy_input_predicts_no_failure_with_low_probability():
    result = predict_failure(**HEALTHY_INPUT)

    assert result["prediction"] == 0
    assert result["probability"] < 0.50


def test_critical_input_predicts_failure_with_high_probability():
    result = predict_failure(**CRITICAL_INPUT)

    assert result["prediction"] == 1
    assert result["probability"] >= 0.75


def test_prediction_is_deterministic_for_the_same_input():
    first = predict_failure(**CRITICAL_INPUT)
    second = predict_failure(**CRITICAL_INPUT)

    assert first["probability"] == second["probability"]
    assert first["prediction"] == second["prediction"]
    assert first["top_factors"] == second["top_factors"]


def test_top_factors_cover_all_five_features_sorted_by_absolute_impact():
    result = predict_failure(**CRITICAL_INPUT)

    factors = result["top_factors"]
    assert len(factors) == 5

    feature_names = {factor["feature"] for factor in factors}
    assert feature_names == {
        "Air temperature [K]",
        "Process temperature [K]",
        "Rotational speed [rpm]",
        "Torque [Nm]",
        "Tool wear [min]",
    }

    impacts = [abs(factor["impact"]) for factor in factors]
    assert impacts == sorted(impacts, reverse=True)


def test_loaded_model_version_and_metadata_are_self_consistent():
    """Not model behavior per se, but the same "did a retrain silently
    change something and nobody noticed" concern: the currently active
    model's own recorded feature list must match what predict.py actually
    feeds it.
    """
    assert model_loader.metadata["feature_columns"] == [
        "Air temperature [K]",
        "Process temperature [K]",
        "Rotational speed [rpm]",
        "Torque [Nm]",
        "Tool wear [min]",
    ]
