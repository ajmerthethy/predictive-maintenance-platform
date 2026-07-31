import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from maintenance_analysis import generate_insights

from lib.api_client import (
    get_machines,
    get_prediction,
    get_maintenance_recommendation,
    get_sensor_readings,
    get_health_score,
    get_downtime_cost,
    get_maintenance_roi,
    get_machine_history,
    get_machine_health,
    get_maintenance_tasks,
    get_explanation,
)
from lib.business_rules import generate_recommendation, format_ai_explanation
from lib.report import generate_maintenance_report

st.set_page_config(
    page_title="Predictive Maintenance Dashboard",
    layout="wide"
)

# -----------------------------
# MACHINE SELECTOR
# -----------------------------

machines = get_machines()

machine_lookup = {
    machine["id"]: machine
    for machine in machines
}

if not machines:

    st.error("No machines found")

    st.stop()

machine_names = {
    machine["name"]: machine["id"]
    for machine in machines
}

selected_machine = st.selectbox(
    "Select Machine",
    machine_names.keys()
)

machine_id = machine_names[selected_machine]
machine_name = machine_lookup.get(
    machine_id,
    "Unknown Machine"
)
selected_machine_data = machine_lookup[machine_id]


# -----------------------------
# ASSET PROFILE
# -----------------------------

st.header(
    f"🏭 {selected_machine}"
)

asset_col1, asset_col2, asset_col3 = st.columns(3)

with asset_col1:

    st.metric(
        "Machine",
        selected_machine_data["name"]
    )

with asset_col2:

    st.metric(
        "Manufacturer",
        selected_machine_data.get(
            "manufacturer",
            "Unknown"
        )
    )

with asset_col3:

    st.metric(
        "Operating Status",
        selected_machine_data.get(
            "status",
            "Unknown"
        )
    )

st.divider()


# -----------------------------
# ASSET HEALTH
# -----------------------------

health_score = get_health_score(machine_id)

st.subheader("🏥 Asset Health")

c1, c2 = st.columns(2)

with c1:

    if health_score:

        st.metric(
            "Health Score",
            f"{health_score['health_score']}/100"
        )

with c2:

    if health_score:

        rating = health_score["rating"]

        # Matches app.services.health_score.calculate_asset_health_score's
        # actual five rating tiers (Excellent/Good/Monitor/At Risk/Critical).
        if rating == "Excellent":
            st.success(rating)

        elif rating == "Good":
            st.success(rating)

        elif rating == "Monitor":
            st.warning(rating)

        elif rating == "At Risk":
            st.warning(rating)

        else:
            st.error(f"🚨 {rating}")

if health_score:

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=health_score["health_score"],
            title={"text": "Asset Health"},
            gauge={
                "axis": {"range": [0, 100]},
                "steps": [
                    {"range": [0, 25], "color": "red"},
                    {"range": [25, 50], "color": "orange"},
                    {"range": [50, 75], "color": "yellow"},
                    {"range": [75, 100], "color": "green"},
                ],
            },
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# -----------------------------
# DETECTED ISSUES
# -----------------------------

health = get_machine_health(machine_id)

st.subheader("⚠️ Detected Issues")

if health and health.get("issues"):

    for issue in health["issues"]:

        st.warning(issue)

else:

    st.success(
        "No abnormal conditions detected"
    )


# -----------------------------
# DOWNTIME COST IMPACT
# -----------------------------

downtime = get_downtime_cost(machine_id)

st.subheader(
    "💰 Downtime Cost Impact"
)

if downtime:

    cost = downtime.get(
        "estimated_daily_cost",
        0
    )

    currency = downtime.get(
        "currency",
        "USD"
    )

    st.metric(
        "Estimated Downtime Exposure",
        f"${cost:,.0f}/day"
    )

else:

    st.info(
        "Downtime estimate unavailable"
    )

# -----------------------------
# MAINTENANCE ROI
# -----------------------------

roi = get_maintenance_roi(machine_id)

if roi:

    st.subheader(
        "💰 Maintenance ROI Analysis"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Preventive Maintenance Cost",
            f"${roi['maintenance_cost']:,.0f}"
        )

    with col2:

        st.metric(
            "Potential Downtime Loss",
            f"${roi['potential_downtime_loss']:,.0f}"
        )

    with col3:

        st.metric(
            "Estimated Savings",
            f"${roi['estimated_savings']:,.0f}"
        )

    st.info(
        f"Recommendation: {roi['recommendation']}"
    )


# -----------------------------
# PREDICTION ANALYSIS / AI DIAGNOSTIC REPORT
# -----------------------------

prediction = get_prediction(
    machine_id
)

st.header(
    "🤖 AI Diagnostic Report"
)

probability_percent = 0

if prediction:

    probability = prediction.get(
        "probability",
        prediction.get(
            "failure_probability",
            prediction.get(
                "prediction_probability",
                0
            )
        )
    )

    probability_percent = probability * 100
    health_score_from_prob = 100 - probability_percent

    # Aligned with the backend's canonical risk_level thresholds
    # (app.services.risk_service.calculate_risk_level: >=75 / >=50).
    if probability_percent >= 75:
        risk_level = "CRITICAL"
        status = "🔴 High Risk"

    elif probability_percent >= 50:
        risk_level = "WARNING"
        status = "🟡 Medium Risk"

    else:
        risk_level = "LOW"
        status = "🟢 Low Risk"

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Failure Probability",
            f"{probability_percent:.1f}%"
        )

    with col2:

        st.metric(
            "Prediction Status",
            status
        )

    with col3:

        st.metric(
            "Machine Health",
            f"{health_score_from_prob:.1f}/100"
        )

    with col4:

        st.metric(
            "Prediction",
            "Failure Detected" if prediction.get("prediction") == 1 else "Normal"
        )

    if "created_at" in prediction:
        st.metric(
            "Prediction Time",
            prediction["created_at"]
        )

    with st.expander("Prediction Details (Developer)"):
        st.json(prediction)

    # Health Gauge

    gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=health_score_from_prob,
            title={
                "text": "Health Score"
            },
            gauge={
                "axis": {
                    "range": [0,100]
                }
            }
        )
    )

    gauge.update_layout(
        height=300
    )

    st.plotly_chart(
        gauge,
        use_container_width=True
    )

    st.subheader("⚙ Current Condition")

    if risk_level == "CRITICAL":

        st.error(
            """
            Critical degradation detected.

            Machine requires immediate inspection.
            """
        )

    elif risk_level == "WARNING":

        st.warning(
            """
            Early signs of degradation detected.

            Preventive maintenance recommended.
            """
        )

    else:

        st.success(
            """
            Machine operating within expected parameters.

            Continue monitoring.
            """
        )

    st.subheader(
        "Why is this machine at risk?"
    )

    factors = format_ai_explanation(
        prediction
    )

    if factors:

        factor_df = pd.DataFrame(
            factors
        )

        st.dataframe(
            factor_df,
            use_container_width=True
        )

        fig = px.bar(
            factor_df,
            x="Impact (%)",
            y="Feature",
            orientation="h",
            title="AI Risk Contributors"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    st.subheader("🔍 Top Factors Influencing Prediction")

    # Support both old and new naming
    raw_factors = prediction.get(
        "top_factors",
        prediction.get(
            "feature_importance",
            []
        )
    )

    if raw_factors:

        factors_df = pd.DataFrame(raw_factors)

        fig = px.bar(
            factors_df,
            x="impact",
            y="feature",
            orientation="h",
            title="SHAP Feature Contributions"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        st.dataframe(
            factors_df,
            use_container_width=True
        )

    else:

        st.info(
            "No explanation factors returned by model."
        )

else:

    st.error(
        "Prediction unavailable."
    )


# -----------------------------
# MAINTENANCE RECOMMENDATION
# -----------------------------

st.subheader(
    "📅 Scheduled Maintenance Recommendation"
)

recommendation = get_maintenance_recommendation(
    machine_id
)

if recommendation:

    priority = recommendation["priority"]

    if priority == "CRITICAL":

        st.error(
            f"🚨 Priority: {priority}"
        )

    elif priority == "HIGH":

        st.warning(
            f"⚠️ Priority: {priority}"
        )

    else:

        st.info(
            f"ℹ️ Priority: {priority}"
        )

    st.write(
        f"""
**Recommended Window**

{recommendation['recommended_window']}


**Recommended Action**

{recommendation['recommended_action']}


**Reason**

"""
    )

    for reason in recommendation["reasons"]:

        st.write(
            f"- {reason}"
        )


# -----------------------------
# PDF REPORT
# -----------------------------

st.subheader(
    "📄 Maintenance Report"
)

if st.button(
    "Generate Maintenance Report PDF"
):

    tasks = get_maintenance_tasks()

    machine_tasks = [

        task for task in tasks

        if task["machine_id"] == machine_id

    ]

    pdf = generate_maintenance_report(
        machine_name,
        health or {},
        prediction or {},
        machine_tasks
    )

    st.download_button(
        label="⬇ Download Report",
        data=pdf,
        file_name=f"{machine_name}_maintenance_report.pdf",
        mime="application/pdf"
    )

    st.divider()


# -----------------------------
# CURRENT SENSOR SNAPSHOT + HISTORY
# -----------------------------

readings = get_sensor_readings(machine_id)

if readings:

    df = pd.DataFrame(readings)

    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )

    df = df.sort_values(
        "timestamp"
    )

else:

    df = pd.DataFrame()

st.header("📡 Current Sensor Status")

if not df.empty:

    latest = df.iloc[-1]

    sensor1, sensor2, sensor3, sensor4, sensor5 = st.columns(5)

    with sensor1:
        st.metric(
            "🌡 Air Temperature",
            f"{latest['air_temperature']:.1f} K"
        )

    with sensor2:
        st.metric(
            "🔥 Process Temperature",
            f"{latest['process_temperature']:.1f} K"
        )

    with sensor3:
        st.metric(
            "⚙ Speed",
            f"{latest['rotational_speed']:.0f} rpm"
        )

    with sensor4:
        st.metric(
            "🔩 Torque",
            f"{latest['torque']:.1f} Nm"
        )

    with sensor5:
        st.metric(
            "🛠 Wear",
            f"{latest['tool_wear']:.0f} min"
        )

else:

    st.warning(
        "No sensor readings available"
    )

st.subheader("📈 Sensor History")

if not df.empty:

    # Air Temperature
    st.subheader("🌡 Air Temperature")
    fig_air = px.line(
        df,
        x="timestamp",
        y="air_temperature",
        title="Air Temperature Over Time",
    )
    st.plotly_chart(fig_air, use_container_width=True)

    # Process Temperature
    st.subheader("🔥 Process Temperature")
    fig_process = px.line(
        df,
        x="timestamp",
        y="process_temperature",
        title="Process Temperature Over Time",
    )
    st.plotly_chart(fig_process, use_container_width=True)

    # Rotational Speed
    st.subheader("⚙ Rotational Speed")
    fig_speed = px.line(
        df,
        x="timestamp",
        y="rotational_speed",
        title="Rotational Speed Over Time",
    )
    st.plotly_chart(fig_speed, use_container_width=True)

    # Torque
    st.subheader("🔩 Torque")
    fig_torque = px.line(
        df,
        x="timestamp",
        y="torque",
        title="Torque Over Time",
    )
    st.plotly_chart(fig_torque, use_container_width=True)

    # Tool Wear
    st.subheader("🛠 Tool Wear")
    fig_wear = px.line(
        df,
        x="timestamp",
        y="tool_wear",
        title="Tool Wear Over Time",
    )
    st.plotly_chart(fig_wear, use_container_width=True)

else:
    st.warning("No sensor readings available")


# -----------------------------
# MACHINE HISTORY
# -----------------------------

st.header("📜 Machine History")

machine_history = get_machine_history(machine_id)

if machine_history:

    st.subheader(
        "🛠 Maintenance History"
    )

    maintenance = machine_history["maintenance"]

    if maintenance:

        maintenance_df = pd.DataFrame(
            maintenance
        )

        st.dataframe(
            maintenance_df,
            use_container_width=True
        )

    else:

        st.info(
            "No maintenance history available"
        )

    st.subheader(
        "🚨 Failure Timeline"
    )

    timeline = []

    for alert in machine_history["alerts"]:

        timeline.append(
            {
                "date": alert["date"],
                "event":
                f"Alert: {alert['message']}",
                "severity":
                alert["severity"]
            }
        )

    for machine_prediction in machine_history["predictions"]:

        timeline.append(
            {
                "date": machine_prediction["date"],
                "event":
                f"Failure prediction probability: {machine_prediction['probability']*100:.1f}%",
                "severity":
                "Prediction"
            }
        )

    timeline_df = pd.DataFrame(
        timeline
    )

    timeline_df = timeline_df.sort_values(
        "date"
    )

    st.dataframe(
        timeline_df,
        use_container_width=True
    )


# -----------------------------
# MAINTENANCE INSIGHTS
# -----------------------------

st.header("🛠 Maintenance Planning")

if not df.empty:

    insights = generate_insights(df)

    insights_recommendation = generate_recommendation(
        insights,
        probability_percent
    )

    st.subheader(
        f"Machine: {selected_machine}"
    )

    st.metric(
        "Maintenance Priority",
        insights_recommendation["priority"]
    )

    st.write("### Detected Conditions")

    for issue in insights_recommendation["issues"]:

        st.write(
            f"⚠ {issue}"
        )

    st.write("### Recommended Action")

    st.info(
        insights_recommendation["timeframe"]
    )

else:

    st.warning(
        "No sensor readings available"
    )


# -----------------------------
# MODEL EXPLANATION
# -----------------------------

st.header("🧠 Why is the model predicting this?")

explanation = get_explanation()

if explanation:

    importance = pd.DataFrame(
        explanation["feature_importance"]
    )

    importance["importance"] = (
        importance["importance"] * 100
    )

    fig = px.bar(
        importance,
        x="importance",
        y="feature",
        orientation="h",
        title="Feature Importance"
    )

    fig.update_layout(
        xaxis_title="Importance (%)",
        yaxis_title="Sensor Feature"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )
