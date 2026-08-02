from app.services.risk_service import calculate_risk_level


def generate_maintenance_recommendation(
    probability,
    health_status,
    trend=None
):

    # CRITICAL/WARNING are decided by the single canonical classifier (see
    # app.services.risk_service.calculate_risk_level) rather than this
    # function's own thresholds, which previously put CRITICAL at 80% -
    # inconsistent with every other panel in the app, which calls a
    # probability of 75-79.9% CRITICAL. MEDIUM/LOW below are a finer-grained
    # split of what the canonical classifier already calls "LOW" - not a
    # competing classification, so they're unaffected by this.
    risk_level = calculate_risk_level(probability)

    risk = probability * 100


    if risk_level == "CRITICAL":

        priority = "CRITICAL"

        timeframe = (
            "Immediate inspection required"
        )

        action = (
            "Inspect machine components "
            "before next operating cycle."
        )


    elif risk_level == "WARNING":

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

        if health_status != "LOW":

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