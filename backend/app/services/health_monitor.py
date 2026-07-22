def calculate_health_status(
        temperature: float,
        vibration: float,
        pressure: float
):

    risk_score = 0
    issues = []

    if temperature > 90:
        risk_score += 40
        issues.append("Critical temperature")

    elif temperature > 80:
        risk_score += 20
        issues.append("High temperature")

    if vibration > 5:
        risk_score += 40
        issues.append("Critical vibration")

    elif vibration > 3:
        risk_score += 20
        issues.append("High vibration")

    if pressure < 50:
        risk_score += 20
        issues.append("Low pressure")

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
            "vibration_change": 0
        }

    first = readings[0]
    last = readings[-1]

    temperature_change = (
        last.temperature - first.temperature
    )

    vibration_change = (
        last.vibration - first.vibration
    )

    if temperature_change > 10 or vibration_change > 2:
        trend = "Deteriorating"
    elif temperature_change > 5 or vibration_change > 1:
        trend = "Warning"
    else:
        trend = "Stable"

    return {
        "trend": trend,
        "temperature_change": round(temperature_change, 2),
        "vibration_change": round(vibration_change, 2)
    }