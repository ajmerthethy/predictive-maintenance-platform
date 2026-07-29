def calculate_downtime_cost(
    machine_status,
    health_score
):

    # Example industrial assumptions
    base_daily_cost = 5000

    if machine_status == "Critical":
        multiplier = 2.5

    elif machine_status == "Warning":
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