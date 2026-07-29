def calculate_maintenance_roi(
    downtime_cost_per_day: float,
    health_score: float,
    maintenance_cost: float = 2500,
    downtime_days: int = 3,
):

    """
    Calculates estimated value of preventive maintenance.
    """

    potential_downtime_loss = (
        downtime_cost_per_day * downtime_days
    )


    avoided_loss = (
        potential_downtime_loss - maintenance_cost
    )


    if avoided_loss < 0:
        avoided_loss = 0


    if health_score < 25:

        recommendation = (
            "Immediate maintenance recommended"
        )

    elif health_score < 50:

        recommendation = (
            "Schedule preventive maintenance"
        )

    else:

        recommendation = (
            "Continue monitoring"
        )


    return {

        "maintenance_cost": maintenance_cost,

        "potential_downtime_loss": round(
            potential_downtime_loss,
            2
        ),

        "estimated_savings": round(
            avoided_loss,
            2
        ),

        "recommendation": recommendation
    }