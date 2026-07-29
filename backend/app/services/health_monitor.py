def calculate_health_status(
        air_temperature: float,
        process_temperature: float,
        rotational_speed: float,
        torque: float,
        tool_wear: float
):

    risk_score = 0
    issues = []

    # Temperature monitoring
    if process_temperature > 330:
        risk_score += 30
        issues.append("Critical process temperature")

    elif process_temperature > 320:
        risk_score += 15
        issues.append("High process temperature")


    # Rotational speed degradation
    if rotational_speed < 1300:
        risk_score += 20
        issues.append("Low rotational speed")

    elif rotational_speed > 1700:
        risk_score += 10
        issues.append("Abnormal rotational speed")


    # Torque stress
    if torque > 70:
        risk_score += 25
        issues.append("High mechanical load")

    elif torque > 60:
        risk_score += 10
        issues.append("Elevated mechanical load")


    # Tool wear
    if tool_wear > 200:
        risk_score += 25
        issues.append("Critical tool wear")

    elif tool_wear > 120:
        risk_score += 10
        issues.append("High tool wear")


    if risk_score >= 70:
        status = "Critical"

    elif risk_score >= 30:
        status = "Warning"

    else:
        status = "Healthy"


    return {
        "status": status,
        "risk_score": risk_score,
        "issues": issues
    }


def analyze_sensor_trend(readings):

    if len(readings) < 2:
        return {
            "trend": "Insufficient data",
            "temperature_change": 0,
            "tool_wear_change": 0
        }


    first = readings[0]
    last = readings[-1]


    temperature_change = (
        last.process_temperature -
        first.process_temperature
    )


    tool_wear_change = (
        last.tool_wear -
        first.tool_wear
    )


    if temperature_change > 10 or tool_wear_change > 50:
        trend = "Deteriorating"

    elif temperature_change > 5 or tool_wear_change > 20:
        trend = "Warning"

    else:
        trend = "Stable"


    return {
        "trend": trend,
        "temperature_change": round(temperature_change, 2),
        "tool_wear_change": round(tool_wear_change, 2)
    }