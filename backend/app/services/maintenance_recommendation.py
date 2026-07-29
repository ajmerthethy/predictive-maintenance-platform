def generate_maintenance_recommendation(
    probability,
    health_status,
    trend=None
):

    risk = probability * 100


    if risk >= 80:

        priority = "CRITICAL"

        timeframe = (
            "Immediate inspection required"
        )

        action = (
            "Inspect machine components "
            "before next operating cycle."
        )


    elif risk >= 50:

        priority = "HIGH"

        timeframe = (
            "Schedule maintenance within 7 days"
        )

        action = (
            "Perform preventive inspection "
            "and check abnormal operating conditions."
        )


    elif risk >= 20:

        priority = "MEDIUM"

        timeframe = (
            "Monitor and inspect within 30 days"
        )

        action = (
            "Continue monitoring sensor trends "
            "and prepare preventive maintenance."
        )


    else:

        priority = "LOW"

        timeframe = (
            "No immediate action required"
        )

        action = (
            "Continue normal operation."
        )


    reasons = []


    if health_status:

        if health_status != "Healthy":

            reasons.append(
                f"Machine status: {health_status}"
            )


    if trend:

        if trend.get("trend") == "Deteriorating":

            reasons.append(
                "Sensor trends indicate deterioration"
            )

        elif trend.get("trend") == "Warning":

            reasons.append(
                "Early degradation detected"
            )


    if not reasons:

        reasons.append(
            "No abnormal conditions detected"
        )


    return {

        "priority": priority,

        "recommended_window": timeframe,

        "recommended_action": action,

        "reasons": reasons

    }