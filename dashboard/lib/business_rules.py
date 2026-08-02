def generate_recommendation(insights, risk_level):
    """`risk_level` is the CRITICAL/WARNING/LOW tier the backend already
    computed (single source of truth: app.services.risk_service.
    calculate_risk_level) - this only maps it to display labels, it does
    not re-derive thresholds from a raw probability (see
    calculate_fleet_status below, which established this pattern first).
    """

    if risk_level == "CRITICAL":
        priority = "🔴 HIGH"
        timeframe = "Immediate inspection required"

    elif risk_level == "WARNING":
        priority = "🟡 MEDIUM"
        timeframe = "Inspect within 7 days"

    else:
        priority = "🟢 LOW"
        timeframe = "Continue monitoring"


    issues = []

    for insight in insights:
        if insight["severity"] != "Low":
            issues.append(
                insight["issue"]
            )


    if not issues:
        issues.append(
            "No abnormal conditions detected"
        )


    return {
        "priority": priority,
        "timeframe": timeframe,
        "issues": issues
    }


def calculate_fleet_status(risk_data):
    """Counts machines by the risk_level the backend already computed
    (single source of truth: app.services.risk_service.calculate_risk_level),
    rather than re-deriving thresholds from the raw probability here.
    """

    critical = 0
    warning = 0
    healthy = 0


    for machine in risk_data:

        risk_level = machine["risk_level"]

        if risk_level == "CRITICAL":
            critical += 1

        elif risk_level == "WARNING":
            warning += 1

        else:
            healthy += 1


    return {
        "critical": critical,
        "warning": warning,
        "healthy": healthy
    }

def format_ai_explanation(prediction):

    if not prediction:
        return []


    factors = prediction.get(
        "top_factors",
        []
    )


    explanations = []


    for factor in factors:

        feature = factor["feature"]
        impact = factor["impact"]


        explanations.append(
            {
                "Feature": feature,
                "Impact (%)": round(
                    abs(impact) * 100,
                    1
                )
            }
        )


    return explanations
