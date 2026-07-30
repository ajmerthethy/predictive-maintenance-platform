from app.services.risk_service import calculate_risk_level


def generate_alert(prediction):

    if calculate_risk_level(prediction.probability) == "CRITICAL":

        return {
            "severity": "HIGH",
            "message": "High failure risk detected",
            "recommended_action":
                "Inspect machine within 24 hours"
        }

    return None