def generate_recommendation(insights, probability_percent):

    if probability_percent > 80:
        priority = "🔴 HIGH"
        timeframe = "Immediate inspection required"

    elif probability_percent > 50:
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

    critical = 0
    warning = 0
    healthy = 0


    for machine in risk_data:

        risk = machine["failure_probability"] * 100


        if risk > 80:
            critical += 1

        elif risk > 50:
            warning += 1

        else:
            healthy += 1


    return {
        "critical": critical,
        "warning": warning,
        "healthy": healthy
    }

def get_risk_level(probability):

    if probability > 80:
        return "🔴 CRITICAL"

    elif probability > 50:
        return "🟡 WARNING"

    else:
        return "🟢 HEALTHY"

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
