



def calculate_asset_health_score(
    failure_probability: float,
    health_status: str,
    active_alerts: int = 0,
    open_work_orders: int = 0,
):
    """
    Returns a health score from 0-100.
    Higher = healthier.
    """

    # Base score from ML prediction
    score = 100 - (failure_probability * 100)

    # Operational penalties
    # Operational penalties
    if health_status == "Critical":
        score -= 10

    elif health_status == "Warning":
        score -= 5

    score -= active_alerts * 2
    score -= open_work_orders * 1

    # Clamp to valid range
    score = max(0, min(100, round(score)))

    # Business-friendly rating
    if score >= 90:
        rating = "Excellent"

    elif score >= 75:
        rating = "Good"

    elif score >= 50:
        rating = "Monitor"

    elif score >= 25:
        rating = "At Risk"

    else:
        rating = "Critical"

    return {
        "health_score": score,
        "rating": rating,
    }