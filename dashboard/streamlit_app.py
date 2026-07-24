import streamlit as st
import requests
import pandas as pd
import plotly.express as px

from maintenance_analysis import generate_insights

import os

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000"
)


st.set_page_config(
    page_title="Predictive Maintenance Dashboard",
    layout="wide"
)


st.title("🏭 Predictive Maintenance Dashboard")



# -----------------------------
# API FUNCTIONS
# -----------------------------

def get_explanation():

    response = requests.get(
        f"{API_URL}/prediction/explanation"
    )

    if response.status_code == 200:
        return response.json()

    return None

def get_machines():

    response = requests.get(
        f"{API_URL}/machines/"
    )

    if response.status_code == 200:
        return response.json()

    return []


def get_prediction(machine_id):

    response = requests.get(
        f"{API_URL}/prediction/machines/{machine_id}"
    )

    if response.status_code == 200:
        return response.json()

    return None



def get_sensor_readings(machine_id):

    response = requests.get(
        f"{API_URL}/sensor_readings/{machine_id}"
    )

    if response.status_code == 200:
        return response.json()

    return []

def get_alerts():

    response = requests.get(
        f"{API_URL}/alerts/"
    )

    if response.status_code == 200:
        return response.json()

    return []



def get_risk_ranking():

    response = requests.get(
        f"{API_URL}/analytics/machines/risk"
    )

    if response.status_code == 200:
        return response.json()

    return []

def get_analytics_summary():

    response = requests.get(
        f"{API_URL}/analytics/summary"
    )

    if response.status_code == 200:
        return response.json()

    return None


def get_maintenance_tasks():

    response = requests.get(
        f"{API_URL}/maintenance/"
    )

    if response.status_code == 200:
        return response.json()

    return []

# -----------------------------
# ANALYTICS SUMMARY KPIs
# -----------------------------

st.header("📈 System Overview")


summary = get_analytics_summary()


if summary:

    col1, col2, col3, col4 = st.columns(4)


    with col1:
        st.metric(
            "Total Predictions",
            summary["total_predictions"]
        )


    with col2:
        st.metric(
            "Failures Detected",
            summary["failures_detected"]
        )


    with col3:
        probability = (
            summary["average_failure_probability"]
            * 100
        )

        st.metric(
            "Average Failure Risk",
            f"{probability:.1f}%"
        )


    with col4:
        st.metric(
            "High Risk Events",
            summary["high_risk_predictions"]
        )

else:

    st.warning(
        "Analytics summary unavailable"
    )

# -----------------------------
# LOAD MACHINES
# -----------------------------

machines = get_machines()


if not machines:

    st.error("No machines found")

    st.stop()



# -----------------------------
# MACHINE SELECTOR
# -----------------------------


machine_names = {
    machine["name"]: machine["id"]
    for machine in machines
}


selected_machine = st.selectbox(
    "Select Machine",
    machine_names.keys()
)


machine_id = machine_names[selected_machine]



# -----------------------------
# FAILURE PREDICTION
# -----------------------------

st.header("Machine Health")


prediction = get_prediction(
    machine_id
)


if prediction:


    probability = (
        prediction["probability"]
        * 100
    )


    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "Failure Risk",
            f"{probability:.1f}%"
        )


    with col2:


        if probability > 80:

            status = "🔴 Critical"

        elif probability > 50:

            status = "🟡 Warning"

        else:

            status = "🟢 Healthy"


        st.metric(
            "Status",
            status
        )

        st.write(prediction)

        st.subheader("🔍 Top Factors Influencing Prediction")

        if "top_factors" in prediction:

            factors_df = pd.DataFrame(prediction["top_factors"])

            fig = px.bar(
                factors_df,
                x="impact",
                y="feature",
                orientation="h",
                title="SHAP Feature Contributions"
            )

            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(factors_df, use_container_width=True)

# -----------------------------
# ACTIVE ALERTS
# -----------------------------

st.header("🚨 Active Alerts")


alerts = get_alerts()


if alerts:

    alerts_df = pd.DataFrame(alerts)

    st.dataframe(
        alerts_df[
            [
                "machine_id",
                "severity",
                "probability",
                "message",
                "recommended_action",
                "status"
            ]
        ],
        use_container_width=True
    )

else:

    st.success("No active alerts")

# -----------------------------
# MAINTENANCE TASKS
# -----------------------------

st.header("🛠 Maintenance Tasks")


tasks = get_maintenance_tasks()


if tasks:

    tasks_df = pd.DataFrame(tasks)


    st.dataframe(
        tasks_df[
            [
                "machine_id",
                "description",
                "technician",
                "status",
                "created_at",
                "completed_at"
            ]
        ],
        use_container_width=True
    )

else:

    st.info("No maintenance tasks found")

# -----------------------------
# SENSOR HISTORY
# -----------------------------

st.header("Sensor History")


readings = get_sensor_readings(
    machine_id
)


if readings:


    df = pd.DataFrame(readings)


    df["timestamp"] = pd.to_datetime(
        df["timestamp"]
    )


    df = df.sort_values(
        "timestamp"
    )


    st.subheader(
        "Temperature"
    )


    fig_temp = px.line(
        df,
        x="timestamp",
        y="air_temperature",
        title="Temperature Over Time"
    )


    st.plotly_chart(
        fig_temp,
        use_container_width=True
    )



    st.subheader(
        "Vibration"
    )


    fig_vibration = px.line(
        df,
        x="timestamp",
        y="vibration",
        title="Vibration Over Time"
    )


    st.plotly_chart(
        fig_vibration,
        use_container_width=True
    )



    st.subheader(
        "Pressure"
    )


    fig_pressure = px.line(
        df,
        x="timestamp",
        y="pressure",
        title="Pressure Over Time"
    )


    st.plotly_chart(
        fig_pressure,
        use_container_width=True
    )


else:

    st.warning(
        "No sensor readings available"
    )



# -----------------------------
# MAINTENANCE INSIGHTS
# -----------------------------


st.header("🛠 Maintenance Insights")

if readings: 

    insights = generate_insights(df)


    for insight in insights:


        if insight["severity"] == "High":

            st.error(
                f"""
                🔴 {insight['issue']}

                Possible cause:
                {insight['cause']}

                Recommended action:
                {insight['action']}
                """
            )


        elif insight["severity"] == "Medium":

            st.warning(
                f"""
                🟡 {insight['issue']}

                Possible cause:
                {insight['cause']}

                Recommended action:
                {insight['action']}
                """
            )


        else:

            st.success(
                f"""
                🟢 {insight['issue']}

                {insight['action']}
                """
            )
else:
    st.warning("No sensor readings available")

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

# -----------------------------
# MACHINE RISK RANKING
# -----------------------------

st.header("📊 Machine Risk Ranking")


risk_data = get_risk_ranking()
st.write(risk_data)


if risk_data:

    risk_df = pd.DataFrame(risk_data)


    fig = px.bar(
        risk_df,
        x="machine_id",
        y="failure_probability",
        color="risk_level",
        title="Machine Failure Risk"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


else:

    st.info("Risk ranking unavailable")

# -----------------------------
# ACTIVE ALERTS
# -----------------------------

st.header("🚨 Active Alerts")


alerts = get_alerts()


if alerts:

    for alert in alerts:

        if alert["severity"] == "HIGH":

            st.error(
                f"""
                🔴 {alert['severity']}

                Machine ID:
                {alert['machine_id']}

                {alert['message']}

                Recommended Action:
                {alert['recommended_action']}
                """
            )

        else:

            st.warning(
                f"""
                🟡 {alert['severity']}

                Machine ID:
                {alert['machine_id']}

                {alert['message']}
                """
            )

else:

    st.success(
        "No active alerts"
    )



# -----------------------------
# MAINTENANCE TASKS
# -----------------------------

st.header("🛠 Maintenance Tasks")


tasks = get_maintenance_tasks()


if tasks:

    tasks_df = pd.DataFrame(tasks)


    st.dataframe(
        tasks_df[
            [
                "machine_id",
                "description",
                "technician",
                "status",
                "created_at",
                "completed_at"
            ]
        ],
        use_container_width=True
    )


else:

    st.info(
        "No maintenance tasks available"
    )