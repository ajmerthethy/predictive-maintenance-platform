def generate_insights(df):

    insights = []


    if df.empty:

        return [
            {
                "severity": "Low",
                "issue": "No sensor data available",
                "cause": "No recent readings found",
                "action": "Check sensor connection"
            }
        ]


    # Analyze latest operational window

    latest = df.tail(50)


    # Current values

    current_temperature = latest["process_temperature"].iloc[-1]

    current_torque = latest["torque"].iloc[-1]

    current_wear = latest["tool_wear"].iloc[-1]

    current_speed = latest["rotational_speed"].iloc[-1]


    # Trend changes

    temperature_change = (
        latest["process_temperature"].iloc[-1]
        -
        latest["process_temperature"].iloc[0]
    )


    torque_change = (
        latest["torque"].iloc[-1]
        -
        latest["torque"].iloc[0]
    )


    wear_change = (
        latest["tool_wear"].iloc[-1]
        -
        latest["tool_wear"].iloc[0]
    )


    speed_change = (
        latest["rotational_speed"].iloc[-1]
        -
        latest["rotational_speed"].iloc[0]
    )


    # -----------------------------
    # Temperature Analysis
    # -----------------------------

    if (
        temperature_change > 5
        or current_temperature > 320
    ):

        insights.append(
            {
                "severity": "High",
                "issue": "Elevated process temperature detected",
                "cause": 
                    "Possible overheating, cooling failure, or increased operating load",
                "action":
                    "Inspect cooling system and thermal controls"
            }
        )


    # -----------------------------
    # Torque Analysis
    # -----------------------------

    if (
        torque_change > 10
        or current_torque > 70
    ):

        insights.append(
            {
                "severity": "High",
                "issue": "Abnormal torque behavior detected",
                "cause":
                    "Possible mechanical resistance, bearing wear, or drivetrain stress",
                "action":
                    "Inspect drive system and mechanical components"
            }
        )


    # -----------------------------
    # Tool Wear Analysis
    # -----------------------------

    if (
        wear_change > 25
        or current_wear > 150
    ):

        insights.append(
            {
                "severity": "Medium",
                "issue":
                    "High tool wear detected",
                "cause":
                    "Component degradation or excessive operating hours",
                "action":
                    "Schedule preventive maintenance and inspect tooling"
            }
        )


    # -----------------------------
    # Rotational Speed Analysis
    # -----------------------------

    if (
        speed_change < -200
        or current_speed < 1200
    ):

        insights.append(
            {
                "severity": "Medium",
                "issue":
                    "Rotational speed instability detected",
                "cause":
                    "Possible motor degradation or increased machine load",
                "action":
                    "Inspect motor, gearbox, and drive components"
            }
        )


    # -----------------------------
    # Combined degradation pattern
    # -----------------------------

    if (
        current_temperature > 315
        and current_torque > 55
        and current_wear > 120
    ):

        insights.append(
            {
                "severity": "High",
                "issue":
                    "Multiple degradation indicators detected",
                "cause":
                    "Temperature, torque, and wear patterns indicate possible machine deterioration",
                "action":
                    "Schedule preventive inspection immediately"
            }
        )


    # Default

    if not insights:

        insights.append(
            {
                "severity": "Low",
                "issue":
                    "No abnormal trends detected",
                "cause":
                    "Machine operating within expected parameters",
                "action":
                    "Continue monitoring"
            }
        )

    # Combined degradation analysis

    if len(insights) >= 3:

        insights = [
            {
                "severity": "High",
                "issue": "Multiple degradation indicators detected",
                "cause": (
                    "Temperature, torque, and wear patterns "
                    "indicate possible machine deterioration"
                ),
                "action": (
                    "Schedule preventive inspection immediately"
                )
            }
        ]


    return insights