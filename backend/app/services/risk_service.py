
def calculate_risk_level(probability):

    if probability >= 0.75:
        return "CRITICAL"

    elif probability >= 0.50:
        return "WARNING"

    return "LOW"
    