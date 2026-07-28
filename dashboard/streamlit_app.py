import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from maintenance_analysis import generate_insights

import os

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

def acknowledge_alert(alert_id):

    response = requests.patch(
        f"{API_URL}/alerts/{alert_id}/acknowledge"
    )

    return response.status_code == 200


def resolve_alert(alert_id):

    response = requests.patch(
        f"{API_URL}/alerts/{alert_id}/resolve"
    )

    return response.status_code == 200

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

def create_maintenance_task(
    machine_id,
    description,
    technician=None,
    alert_id=None
):

    response = requests.post(
        f"{API_URL}/maintenance/",
        params={
            "machine_id": machine_id,
            "description": description,
            "technician": technician,
            "alert_id": alert_id
        }
    )

    return response.status_code == 200

def get_alert_history():

    response = requests.get(
        f"{API_URL}/alerts/?status=RESOLVED"
    )

    if response.status_code == 200:
        return response.json()

    return []

# -----------------------------
# FLEET OVERVIEW
# -----------------------------

st.header("🏭 Fleet Overview")


risk_data = get_risk_ranking()


if risk_data:

    fleet_status = calculate_fleet_status(
        risk_data
    )


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Total Machines",
            len(risk_data)
        )


    with col2:

        st.metric(
            "🟢 Healthy",
            fleet_status["healthy"]
        )


    with col3:

        st.metric(
            "🟡 Warning",
            fleet_status["warning"]
        )


    with col4:

        st.metric(
            "🔴 Critical",
            fleet_status["critical"]
        )
risk_df = pd.DataFrame(risk_data)

risk_df["failure_probability"] = (
    risk_df["failure_probability"] * 100
)

risk_df = risk_df.sort_values(
    "failure_probability",
    ascending=False
)

highest = risk_df.iloc[0]

st.warning(
    f"""
### 🚨 Highest Priority Asset

**{highest['machine_name']}**

Failure Risk: **{highest['failure_probability']:.1f}%**

Current Status: **{highest['risk_level']}**

Recommended Action:
{"Immediate inspection required" if highest["failure_probability"] > 80 else "Inspect within 7 days"}
"""
)



fleet_fig = px.pie(
    names=["Healthy", "Warning", "Critical"],
    values=[
        fleet_status["healthy"],
        fleet_status["warning"],
        fleet_status["critical"],
    ],
    hole=0.6,
    title="Fleet Health Distribution"
)

st.plotly_chart(
    fleet_fig,
    use_container_width=True
)

# -----------------------------
# FLEET STATUS BREAKDOWN
# -----------------------------

st.header("🚦 Fleet Status Overview")


if risk_data:

    critical_machines = []
    warning_machines = []
    healthy_machines = []


    for machine in risk_data:

        risk = machine["failure_probability"] * 100


        machine_info = {
            "name": machine["machine_name"],
            "risk": risk,
            "last_prediction": machine["last_prediction"]
        }


        if risk > 80:

            critical_machines.append(machine_info)

        elif risk > 50:

            warning_machines.append(machine_info)

        else:

            healthy_machines.append(machine_info)


    col1, col2, col3 = st.columns(3)


    # -----------------------------
    # CRITICAL MACHINES
    # -----------------------------

    with col1:

        st.subheader("🔴 Critical")

        if critical_machines:

            for machine in critical_machines:

                st.error(
                    f"""
**{machine['name']}**

Failure Risk:
{machine['risk']:.1f}%

Immediate inspection required
"""
                )

        else:

            st.success(
                "No critical machines"
            )


    # -----------------------------
    # WARNING MACHINES
    # -----------------------------

    with col2:

        st.subheader("🟡 Warning")

        if warning_machines:

            for machine in warning_machines:

                st.warning(
                    f"""
**{machine['name']}**

Failure Risk:
{machine['risk']:.1f}%

Inspection recommended
"""
                )

        else:

            st.success(
                "No warning machines"
            )


    # -----------------------------
    # HEALTHY MACHINES
    # -----------------------------

    with col3:

        st.subheader("🟢 Healthy")

        if healthy_machines:

            for machine in healthy_machines:

                st.success(
                    f"""
**{machine['name']}**

Failure Risk:
{machine['risk']:.1f}%

Operating normally
"""
                )

        else:

            st.info(
                "No healthy machines"
            )


else:

    st.info(
        "Fleet data unavailable"
    )

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

machine_lookup = {
    machine["id"]: machine
    for machine in machines
}


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

selected_machine_data = machine_lookup[machine_id]

# -----------------------------
# MACHINE DETAIL NAVIGATION
# -----------------------------

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🏭 Overview",
        "📈 Sensors",
        "🤖 Prediction",
        "🛠 Maintenance"
    ]
)



# -----------------------------
# FAILURE PREDICTION
# -----------------------------

with tab1:

    st.header("🏭 Asset Profile")

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

with tab3:

    st.header("🤖 Prediction Analysis")


prediction = get_prediction(
    machine_id
)


if prediction:

    # Handle different API response formats
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

    health_score = 100 - probability_percent


    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "Failure Risk",
            f"{probability_percent:.1f}%"
        )


    with col2:

        st.metric(
            "Machine Health",
            f"{health_score:.1f}/100"
        )


    # Health Gauge

    gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=health_score,
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


    with col3:

        st.metric(
            "Risk Level",
            get_risk_level(probability_percent)
        )


    with col4:

        st.metric(
            "Prediction",
            "Failure Detected" if probability > 0.5 else "Normal"
        )
    if "created_at" in prediction:
        st.metric(
            "Prediction Time",
            prediction["created_at"]
        )
    with st.expander("Prediction Details (Developer)"):
        st.json(prediction)

    st.subheader("⚙ Current Condition")


    if probability_percent > 80:

        st.error(
            """
            Critical degradation detected.

            Machine requires immediate inspection.
            """
        )


    elif probability_percent > 50:

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


    st.subheader("🔍 Top Factors Influencing Prediction")


    # Support both old and new naming
    factors = prediction.get(
        "top_factors",
        prediction.get(
            "feature_importance",
            []
        )
    )


    if factors:

        factors_df = pd.DataFrame(factors)


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
# ACTIVE ALERTS
# -----------------------------

st.header("🚨 Active Alerts")

alerts = get_alerts()



if alerts:

    for alert in alerts:

        machine_name = machine_lookup.get(
            alert["machine_id"],
            {}
        ).get(
            "name",
            f"Machine {alert['machine_id']}"
        )

        severity = alert["severity"]
        status = alert["status"]

        container = st.container()

        with container:

            col1, col2, col3, col4 = st.columns([5,1,1,1])

            with col1:

                if severity == "HIGH":

                    severity_icon = {
                        "HIGH": "🔴",
                        "MEDIUM": "🟡",
                        "LOW": "🟢"
                    }.get(alert["severity"], "⚪")

                    st.error(
                        f"""
### {severity_icon} {alert["severity"]}

**Machine:** {machine_name}

**Failure Risk:** {alert['probability']*100:.1f}%

**Status:** {status}

{alert['message']}

**Recommended Action**

{alert['recommended_action']}
"""
                    )

                else:

                    st.warning(
                        f"""
### 🟡 {severity}

**Machine ID:** {alert['machine_id']}

**Status:** {status}

**Created**

{alert["created_at"]}

{alert['message']}

**Recommended Action**

{alert['recommended_action']}
"""
                    )

            with col2:

                if status == "OPEN":

                    if st.button(
                        "Acknowledge",
                        key=f"ack_{alert['id']}"
                    ):

                        if acknowledge_alert(alert["id"]):

                            st.success(
                                "Alert acknowledged."
                            )

                            st.rerun()

            with col3:

                if status != "RESOLVED":

                    if st.button(
                        "Resolve",
                        key=f"resolve_{alert['id']}"
                    ):

                        if resolve_alert(alert["id"]):

                            st.success(
                                "Alert resolved."
                            )

                            st.rerun()

            with col4:

                if st.button(
                    "🛠 Work Order",
                    key=f"task_{alert['id']}"
                ):

                    description = (
                        alert["recommended_action"]
                    )

                    if create_maintenance_task(
                        machine_id=alert["machine_id"],
                        description=description,
                        technician="Unassigned",
                        alert_id=alert["id"]
                    ):

                        st.success(
                            "Maintenance task created"
                        )

                        st.rerun()

            st.divider()

else:

    st.success(
        "✅ No active alerts."
    )

# -----------------------------
# ALERT HISTORY
# -----------------------------

st.header("📜 Alert History")


history = get_alert_history()


if history:

    history_df = pd.DataFrame(history)


    st.dataframe(
        history_df[
            [
                "machine_id",
                "severity",
                "message",
                "status",
                "created_at",
                "resolved_at"
            ]
        ],
        use_container_width=True
    )


else:

    st.info(
        "No resolved alerts yet"
    )

# -----------------------------
# MAINTENANCE TASKS
# -----------------------------

st.header("🛠 Maintenance Work Orders")


tasks = get_maintenance_tasks()


if tasks:

    tasks_df = pd.DataFrame(tasks)


    for _, task in tasks_df.iterrows():

        with st.container():

            st.subheader(
                f"Work Order #{task['id']}"
            )


            col1, col2, col3 = st.columns(3)


            # -----------------------------
            # WORK ORDER DETAILS
            # -----------------------------

            with col1:

                st.write(
                    f"**Machine ID:** {task['machine_id']}"
                )

                st.write(
                    f"**Description:** {task['description']}"
                )


                if task.get("alert_id"):

                    st.write(
                        f"**Linked Alert:** #{task['alert_id']}"
                    )


            # -----------------------------
            # STATUS
            # -----------------------------

            with col2:

                status = task.get(
                    "status",
                    "OPEN"
                )


                if status == "COMPLETED":

                    st.success(
                        "🟢 COMPLETED"
                    )


                elif status == "IN_PROGRESS":

                    st.warning(
                        "🟡 IN PROGRESS"
                    )


                else:

                    st.info(
                        "🔵 OPEN"
                    )


                st.write(
                    f"Technician: {task.get('technician','Unassigned')}"
                )


                if task.get("completed_at"):

                    st.write(
                        f"Completed: {task['completed_at']}"
                    )


            # -----------------------------
            # ACTION BUTTONS
            # -----------------------------

            with col3:


                # OPEN → IN_PROGRESS

                if status == "OPEN":


                    if st.button(
                        "▶ Start Work",
                        key=f"start_{task['id']}"
                    ):


                        response = requests.patch(
                            f"{API_URL}/maintenance/{task['id']}/start",
                            params={
                                "technician": "Maintenance Team"
                            }
                        )


                        if response.status_code == 200:

                            st.success(
                                "Work order started"
                            )

                            st.rerun()


                        else:

                            st.error(
                                "Failed to start work order"
                            )



                # IN_PROGRESS → COMPLETED

                elif status == "IN_PROGRESS":


                    if st.button(
                        "✅ Complete Work",
                        key=f"complete_{task['id']}"
                    ):


                        response = requests.patch(
                            f"{API_URL}/maintenance/{task['id']}/complete"
                        )


                        if response.status_code == 200:

                            st.success(
                                "Work order completed"
                            )

                            st.rerun()


                        else:

                            st.error(
                                "Failed to complete task"
                            )



                # COMPLETED

                else:

                    st.write(
                        "No actions available"
                    )


            st.divider()


else:

    st.info(
        "No maintenance work orders found"
    )
# -----------------------------
# LOAD SENSOR DATA
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



# -----------------------------
# CURRENT SENSOR SNAPSHOT
# -----------------------------

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


# -----------------------------
# SENSOR HISTORY
# -----------------------------


with tab2:

    st.header("📈 Sensor History")

readings = get_sensor_readings(machine_id)

if readings:

    df = pd.DataFrame(readings)

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

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
# MAINTENANCE INSIGHTS
# -----------------------------

with tab4:

    st.header("🛠 Maintenance Planning")


if not df.empty:

    insights = generate_insights(df)

    recommendation = generate_recommendation(
        insights,
        probability_percent
    )


    st.subheader(
        f"Machine: {selected_machine}"
    )


    st.metric(
        "Maintenance Priority",
        recommendation["priority"]
    )


    st.write("### Detected Conditions")

    for issue in recommendation["issues"]:

        st.write(
            f"⚠ {issue}"
        )


    st.write("### Recommended Action")

    st.info(
        recommendation["timeframe"]
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

# -----------------------------
# MACHINE RISK RANKING
# -----------------------------

st.header("📊 Machine Risk Ranking")


risk_data = get_risk_ranking()


if risk_data:

    risk_df = pd.DataFrame(risk_data)


    # Convert probability to percentage
    risk_df["failure_probability"] = (
        risk_df["failure_probability"] * 100
    ).round(1)


    # Calculate health score
    risk_df["health_score"] = (
        100 - risk_df["failure_probability"]
    ).round(1)


    # Generate recommendations
    def get_action(risk):

        if risk > 80:
            return "🔴 Immediate inspection required"

        elif risk > 50:
            return "🟡 Inspect within 7 days"

        else:
            return "🟢 Continue monitoring"


    risk_df["recommended_action"] = (
        risk_df["failure_probability"]
        .apply(get_action)
    )


    # Rename columns
    risk_df = risk_df.rename(
        columns={
            "machine_name": "Machine",
            "failure_probability": "Failure Risk (%)",
            "risk_level": "Risk Level",
            "last_prediction": "Last Prediction",
            "health_score": "Health Score"
        }
    )


    # Sort highest risk first
    risk_df = risk_df.sort_values(
        by="Failure Risk (%)",
        ascending=False
    )


    # Display table

    styled = (
        risk_df[
            [
                "Machine",
                "Failure Risk (%)",
                "Health Score",
                "Risk Level",
                "recommended_action",
                "Last Prediction"
            ]
        ]
        .style
        .background_gradient(
            subset=["Failure Risk (%)"],
            cmap="Reds"
        )
    )

    st.dataframe(
        styled,
        use_container_width=True
    )


    # Risk visualization

    fig = px.bar(
        risk_df,
        x="Machine",
        y="Failure Risk (%)",
        color="Risk Level",
        title="Machine Failure Risk Ranking"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


else:

    st.info(
        "Risk ranking unavailable"
    )

fleet_health = risk_df["Health Score"].mean()

st.metric(
    "Fleet Health Score",
    f"{fleet_health:.1f}/100"
)