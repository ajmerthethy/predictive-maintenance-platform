from app.core.config import DOWNTIME_BASE_DAILY_COST


def calculate_downtime_cost(
    machine_status,
    health_score
):

    base_daily_cost = DOWNTIME_BASE_DAILY_COST

    if machine_status == "CRITICAL":
        multiplier = 2.5

    elif machine_status == "WARNING":
        multiplier = 1.5

    else:
        multiplier = 1


    risk_factor = (100 - health_score) / 100


    estimated_cost = (
        base_daily_cost
        * multiplier
        * risk_factor
    )


    return {
        "estimated_daily_cost": round(
            estimated_cost,
            2
        ),
        "currency": "USD"
    }