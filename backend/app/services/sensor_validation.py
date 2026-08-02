"""Physical plausibility bounds for the five sensor inputs the model
consumes. Deliberately generous - not the AI4I training data's narrow
observed range (that would be a drift-detection concern, a separate,
harder problem) - the goal here is only to catch garbage/impossible values
(a negative Kelvin reading, a six-digit typo) before they reach the model,
not to constrain inputs to what the model happened to be trained on.

Callers must run this AFTER any tenancy/ownership check, not before - it is
intentionally not enforced at the Pydantic schema layer, so that an
ownership failure (wrong account, forged machine_id) is reported as 404/403
regardless of how implausible the accompanying sensor values are.
"""

SENSOR_RANGES = {
    "air_temperature": (250.0, 400.0, "K"),
    "process_temperature": (250.0, 500.0, "K"),
    "rotational_speed": (0.0, 10000.0, "rpm"),
    "torque": (0.0, 1000.0, "Nm"),
    "tool_wear": (0.0, 1000.0, "min"),
}


def out_of_range_fields(
    air_temperature,
    process_temperature,
    rotational_speed,
    torque,
    tool_wear,
):
    """Return a list of (field, value, low, high, unit) tuples for every
    field outside its plausible range. Empty list means all five are fine.
    """

    values = {
        "air_temperature": air_temperature,
        "process_temperature": process_temperature,
        "rotational_speed": rotational_speed,
        "torque": torque,
        "tool_wear": tool_wear,
    }

    violations = []

    for field, value in values.items():

        low, high, unit = SENSOR_RANGES[field]

        if value < low or value > high:
            violations.append((field, value, low, high, unit))

    return violations


def violation_messages(violations):
    """Render out_of_range_fields()'s tuples as human-readable strings."""

    return [
        f"{field} value {value} is outside the realistic range "
        f"[{low}, {high}] {unit}"
        for field, value, low, high, unit in violations
    ]
