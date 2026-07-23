
def generate_alert(prediction):

    if prediction.probability >= 0.75:

        return {
            "severity": "HIGH",
            "message": "High failure risk detected",
            "recommended_action":
                "Inspect machine within 24 hours"
        }

    return None