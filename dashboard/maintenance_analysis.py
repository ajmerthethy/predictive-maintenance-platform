import pandas as pd


def generate_insights(df):

    insights = []


    # Use latest readings
    latest = df.tail(50)


    # Calculate trends

    vibration_change = (
        latest["vibration"].iloc[-1]
        -
        latest["vibration"].iloc[0]
    )


    temperature_change = (
        latest["temperature"].iloc[-1]
        -
        latest["temperature"].iloc[0]
    )


    pressure_change = (
        latest["pressure"].iloc[-1]
        -
        latest["pressure"].iloc[0]
    )


    # Vibration analysis

    if vibration_change > 0.5:

        insights.append(
            {
                "severity": "High",
                "issue": "Increasing vibration detected",
                "cause": "Possible bearing or mechanical wear",
                "action": "Inspect bearings and moving components"
            }
        )


    # Temperature analysis

    if temperature_change > 5:

        insights.append(
            {
                "severity": "Medium",
                "issue": "Temperature rising",
                "cause": "Possible overheating or increased load",
                "action": "Inspect cooling system"
            }
        )


    # Pressure analysis

    if pressure_change < -5:

        insights.append(
            {
                "severity": "Medium",
                "issue": "Pressure dropping",
                "cause": "Possible leak or hydraulic degradation",
                "action": "Inspect hydraulic lines"
            }
        )


    if not insights:

        insights.append(
            {
                "severity": "Low",
                "issue": "No abnormal trends detected",
                "cause": "Machine operating normally",
                "action": "Continue monitoring"
            }
        )


    return insights