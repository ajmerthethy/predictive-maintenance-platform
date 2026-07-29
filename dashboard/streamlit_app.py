import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from maintenance_analysis import generate_insights

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO

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

if "page" not in st.session_state:
    st.session_state.page = "fleet"


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
def generate_maintenance_report(
    machine_name,
    health,
    prediction,
    tasks
):

    buffer = BytesIO()


    doc = SimpleDocTemplate(
        buffer
    )


    styles = getSampleStyleSheet()

    story = []


    story.append(
        Paragraph(
            f"Predictive Maintenance Report - {machine_name}",
            styles["Title"]
        )
    )


    story.append(
        Spacer(1, 12)
    )


    # Health Summary

    story.append(
        Paragraph(
            f"""
            <b>Machine:</b> {machine_name}<br/>
            <b>Status:</b> {health.get('status','Unknown')}<br/>
            <b>Risk Score:</b> {prediction.get('probability',0)*100:.1f}%<br/>
            """,
            styles["BodyText"]
        )
    )


    story.append(
        Spacer(1, 12)
    )


    # AI Diagnosis

    story.append(
        Paragraph(
            "AI Diagnostic Factors",
            styles["Heading2"]
        )
    )


    for factor in prediction.get(
        "top_factors",
        []
    ):

        story.append(
            Paragraph(
                f"""
                {factor['feature']}
                Impact:
                {factor['impact']*100:.1f}%
                """,
                styles["BodyText"]
            )
        )


    story.append(
        Spacer(1, 12)
    )


    # Maintenance History

    story.append(
        Paragraph(
            "Maintenance History",
            styles["Heading2"]
        )
    )


    if tasks:

        for task in tasks:

            story.append(
                Paragraph(
                    f"""
                    Work Order:
                    {task['description']}<br/>

                    Status:
                    {task['status']}<br/>

                    Technician:
                    {task.get('technician','Unassigned')}
                    """,
                    styles["BodyText"]
                )
            )

            story.append(
                Spacer(1,8)
            )

    else:

        story.append(
            Paragraph(
                "No maintenance history recorded.",
                styles["BodyText"]
            )
        )


    doc.build(
        story
    )


    buffer.seek(0)


    return buffer

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

def get_maintenance_recommendation(machine_id):

    response = requests.get(
        f"{API_URL}/recommendations/machines/{machine_id}"
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

def get_health_score(machine_id):

    response = requests.get(
        f"{API_URL}/health-score/machines/{machine_id}"
    )

    if response.status_code == 200:
        return response.json()

    return None

def get_downtime_cost(machine_id):

    response = requests.get(
        f"{API_URL}/downtime/machines/{machine_id}"
    )

    if response.status_code == 200:
        return response.json()

    return None

def get_maintenance_roi(machine_id):

    response = requests.get(
        f"{API_URL}/roi/machines/{machine_id}"
    )

    if response.status_code == 200:
        return response.json()

    return None

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

def get_machine_history(machine_id):

    response = requests.get(
        f"{API_URL}/history/machines/{machine_id}"
    )

    if response.status_code == 200:
        return response.json()

    return None

def get_machine_prediction(machine_id):

    response = requests.get(
        f"{API_URL}/prediction/machines/{machine_id}"
    )

    if response.status_code == 200:
        return response.json()

    return None

def get_machine_health(machine_id):

    response = requests.get(
        f"{API_URL}/machines/{machine_id}/health"
    )

    if response.status_code == 200:
        return response.json()

    return None

def get_machine_trend(machine_id):

    response = requests.get(
        f"{API_URL}/machines/{machine_id}/trend"
    )

    if response.status_code == 200:
        return response.json()

    return None

def get_executive_summary():

    response = requests.get(
        f"{API_URL}/executive/summary"
    )

    if response.status_code == 200:
        return response.json()

    return None

def get_maintenance_intelligence():

    response = requests.get(
        f"{API_URL}/maintenance-intelligence/summary"
    )

    if response.status_code == 200:
        return response.json()

    return None

def get_fleet_risk():

    response = requests.get(
        f"{API_URL}/fleet-risk/summary"
    )

    if response.status_code == 200:
        return response.json()

    return None

def machine_detail(machine_id):

    machine_name = machine_lookup.get(
        machine_id,
        "Unknown Machine"
    )

    health_score = get_health_score(machine_id)
    downtime = get_downtime_cost(machine_id)
    roi = get_maintenance_roi(machine_id)


    st.header(
        f"🏭 {machine_name}"
    )

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

            if rating == "Excellent":
                st.success(rating)

            elif rating == "Good":
                st.success(rating)

            elif rating == "Fair":
                st.warning(rating)

            elif rating == "Poor":
                st.error(rating)

            else:
                st.error("🚨 Critical")

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
    # HEALTH SUMMARY
    # -----------------------------

    health = get_machine_health(
        machine_id
    )


    prediction = get_prediction(
        machine_id
    )


    if health and prediction:


        risk = prediction["probability"] * 100

        health_score = 100 - risk


        c1, c2, c3 = st.columns(3)


        with c1:

            st.metric(
                "Machine Status",
                health["status"]
            )


        with c2:

            st.metric(
                "Failure Risk",
                f"{risk:.1f}%"
            )


        with c3:

            st.metric(
                "Health Score",
                f"{health_score:.1f}%"
            )



    st.divider()



    # -----------------------------
    # AI DIAGNOSIS
    # -----------------------------

    st.subheader(
        "🤖 AI Diagnosis"
    )


    if prediction:


        factors = prediction.get(
            "top_factors",
            []
        )


        if factors:


            for factor in factors:

                impact = factor["impact"]


                if impact > 0:

                    st.warning(
                        f"""
⚠️ **{factor['feature']}**

Risk contribution:
+{impact*100:.1f}%
"""
                    )


                else:

                    st.success(
                        f"""
✅ **{factor['feature']}**

Impact:
{impact*100:.1f}%
"""
                    )


        else:

            st.info(
                "No diagnostic factors available."
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
            health,
            prediction,
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
    # SENSOR TREND
    # -----------------------------

    st.subheader(
        "📈 Sensor Trend"
    )


    readings = get_sensor_readings(
        machine_id
    )


    if readings:

        df = pd.DataFrame(
            readings
        )


        df["timestamp"] = pd.to_datetime(
            df["timestamp"]
        )


        sensor = st.selectbox(
            "Select Sensor",
            [
                "air_temperature",
                "process_temperature",
                "rotational_speed",
                "torque",
                "tool_wear"
            ]
        )


        fig = px.line(
            df,
            x="timestamp",
            y=sensor,
            title=f"{sensor} History"
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    else:

        st.info(
            "No sensor data available."
        )



    st.divider()



    # -----------------------------
    # MAINTENANCE HISTORY
    # -----------------------------

    st.subheader(
        "🛠 Maintenance History"
    )


    tasks = get_maintenance_tasks()


    machine_tasks = [

        task for task in tasks

        if task["machine_id"] == machine_id

    ]


    if machine_tasks:


        history = pd.DataFrame(
            machine_tasks
        )


        st.dataframe(
            history[
                [
                    "description",
                    "status",
                    "technician",
                    "created_at"
                ]
            ],
            use_container_width=True
        )


    else:

        st.info(
            "No maintenance history."
        )

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
# ASSET RISK RANKING
# -----------------------------

st.subheader(
    "🏭 Asset Risk Ranking"
)


risk_bar = px.bar(
    risk_df,
    x="machine_name",
    y="failure_probability",
    color="risk_level",
    text="failure_probability",
    title="Failure Risk by Asset"
)


risk_bar.update_layout(
    xaxis_title="Asset",
    yaxis_title="Failure Risk (%)"
)


st.plotly_chart(
    risk_bar,
    use_container_width=True
)

# -----------------------------
# MAINTENANCE INTELLIGENCE
# -----------------------------

st.divider()

st.header(
    "🛠 Maintenance Intelligence"
)


maintenance_data = (
    get_maintenance_intelligence()
)


if maintenance_data:

    actions = maintenance_data[
        "actions_required"
    ]


    if actions:

        for asset in actions:

            st.warning(
                f"""
### 🚨 {asset['machine_name']}

Failure Risk:
**{asset['risk']}%**

Recommended Action:

{asset['recommendation']}
"""
            )

    else:

        st.success(
            "No immediate maintenance actions required."
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

def executive_dashboard():

    st.header(
        "📊 Executive Dashboard"
    )

    data = get_executive_summary()

    if not data:
        st.error(
            "Executive analytics unavailable"
        )
        return


    # KPI CARDS

    col1, col2, col3, col4 = st.columns(4)


    with col1:
        st.metric(
            "Fleet Health Score",
            f"{data['fleet_health_score']}/100"
        )


    with col2:
        st.metric(
            "Critical Assets",
            data["critical_assets"]
        )


    with col3:
        st.metric(
            "Open Work Orders",
            data["open_work_orders"]
        )


    with col4:
        st.metric(
            "Active Alerts",
            data["active_alerts"]
        )


    st.divider()


    # FINANCIAL IMPACT

    st.subheader(
        "💰 Financial Impact"
    )


    c1, c2 = st.columns(2)


    with c1:

        st.metric(
            "Downtime Exposure",
            f"${data['downtime_exposure']:,.0f}"
        )


    with c2:

        st.metric(
            "Potential Savings",
            f"${data['potential_savings']:,.0f}"
        )
    st.divider()

    st.subheader(
        "🚦 Fleet Risk Overview"
    )


    risk_data = get_fleet_risk()


    if risk_data:

        distribution = risk_data["distribution"]


        col1, col2, col3 = st.columns(3)


        with col1:
            st.metric(
                "🟢 Healthy Assets",
                distribution["healthy"]
            )


        with col2:
            st.metric(
                "🟡 Warning Assets",
                distribution["warning"]
            )


        with col3:
            st.metric(
                "🔴 Critical Assets",
                distribution["critical"]
            )

    st.subheader(
        "🏭 Asset Risk Ranking"
    )


    assets = pd.DataFrame(
        risk_data["assets"]
    )


    st.dataframe(
        assets,
        use_container_width=True
    )


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

if st.button(
    "🔎 View Machine Details"
):

    st.session_state.page = "machine_detail"



machine_id = machine_names[selected_machine]

page = st.sidebar.selectbox(
    "Navigation",
    [
        "Fleet Overview",
        "Machine Detail",
        "Executive Dashboard"
    ]
)

if page == "Machine Detail":

    machine_detail(
        machine_id
    )
elif page == "Executive Dashboard":

    executive_dashboard()

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

st.header("🤖 AI Diagnostic Report")


if prediction:

    probability = (
        prediction["probability"] * 100
    )


    if probability > 80:
        status = "🔴 High Risk"

    elif probability > 50:
        status = "🟡 Medium Risk"

    else:
        status = "🟢 Low Risk"


    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "Failure Probability",
            f"{probability:.1f}%"
        )


    with col2:

        st.metric(
            "Prediction Status",
            status
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


    # -----------------------------
    # MAINTENANCE KPI CARDS
    # -----------------------------

    total_tasks = len(tasks_df)

    open_tasks = len(
        tasks_df[
            tasks_df["status"] == "OPEN"
        ]
    )

    progress_tasks = len(
        tasks_df[
            tasks_df["status"] == "IN_PROGRESS"
        ]
    )

    completed_tasks = len(
        tasks_df[
            tasks_df["status"] == "COMPLETED"
        ]
    )


    st.subheader(
        "📊 Operations Overview"
    )


    k1, k2, k3, k4 = st.columns(4)


    with k1:
        st.metric(
            "Total Work Orders",
            total_tasks
        )


    with k2:
        st.metric(
            "🔵 Open",
            open_tasks
        )


    with k3:
        st.metric(
            "🟡 In Progress",
            progress_tasks
        )


    with k4:
        st.metric(
            "🟢 Completed",
            completed_tasks
        )


    st.divider()


    # -----------------------------
    # WORK ORDER DETAILS
    # -----------------------------

    for _, task in tasks_df.iterrows():

        machine_name = machine_lookup.get(
            task["machine_id"],
            f"Machine {task['machine_id']}"
        )


        with st.container():

            st.subheader(
                f"Work Order #{task['id']} — {machine_name}"
            )


            col1, col2, col3 = st.columns(3)


            # -----------------------------
            # DETAILS
            # -----------------------------

            with col1:

                st.write(
                    f"**Machine:** 🏭 {machine_name}"
                )


                st.write(
                    f"**Description:** {task['description']}"
                )


                if "URGENT" in task["description"]:

                    st.error(
                        "🚨 Priority: CRITICAL"
                    )

                elif "Preventive" in task["description"]:

                    st.warning(
                        "⚠️ Priority: MEDIUM"
                    )

                else:

                    st.info(
                        "ℹ️ Priority: NORMAL"
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
# MACHINE HISTORY
# -----------------------------

st.header("📜 Machine History")


history = get_machine_history(machine_id)


if history:


    st.subheader(
        "🛠 Maintenance History"
    )


    maintenance = history["maintenance"]


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


    for alert in history["alerts"]:

        timeline.append(
            {
                "date": alert["date"],
                "event":
                f"Alert: {alert['message']}",
                "severity":
                alert["severity"]
            }
        )


    for prediction in history["predictions"]:

        timeline.append(
            {
                "date": prediction["date"],
                "event":
                f"Failure prediction probability: {prediction['probability']*100:.1f}%",
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

# ==================================
# MACHINE DETAIL PAGE
# ==================================

if st.session_state.page == "machine_detail":


    st.header(
        f"🏭 {selected_machine}"
    )


    st.button(
        "⬅ Back to Fleet",
        on_click=lambda:
        st.session_state.update(
            page="fleet"
        )
    )


    health = get_machine_health(
        machine_id
    )


    prediction = get_machine_prediction(
        machine_id
    )


    if health and prediction:


        risk = prediction["probability"] * 100

        health_score = 100 - risk


        st.subheader(
            "Asset Health Profile"
        )


        c1, c2, c3 = st.columns(3)


        with c1:

            st.metric(
                "Failure Risk",
                f"{risk:.1f}%"
            )


        with c2:

            st.metric(
                "Health Score",
                f"{health_score:.1f}%"
            )


        with c3:

            st.metric(
                "Status",
                health["status"]
            )



        st.divider()


        # --------------------------
        # AI DIAGNOSIS
        # --------------------------

        st.subheader(
            "🤖 AI Diagnosis"
        )


        factors = prediction.get(
            "top_factors",
            []
        )


        if factors:

            factor_df = pd.DataFrame(
                factors
            )


            st.dataframe(
                factor_df,
                use_container_width=True
            )



        # --------------------------
        # ISSUES
        # --------------------------

        st.subheader(
            "⚠️ Detected Issues"
        )


        if health["issues"]:

            for issue in health["issues"]:

                st.warning(issue)

        else:

            st.success(
                "No abnormal conditions detected"
            )



        st.divider()


        # --------------------------
        # SENSOR DATA
        # --------------------------

        st.subheader(
            "📈 Sensor History"
        )


        readings = get_sensor_readings(
            machine_id
        )


        if readings:

            df = pd.DataFrame(
                readings
            )


            fig = px.line(
                df,
                x="timestamp",
                y="torque",
                title="Torque Trend"
            )


            st.plotly_chart(
                fig,
                use_container_width=True
            )


        st.divider()


        # --------------------------
        # HISTORY
        # --------------------------

        st.subheader(
            "📜 Maintenance History"
        )


        history = get_machine_history(
            machine_id
        )


        if history:

            maintenance_df = pd.DataFrame(
                history["maintenance"]
            )


            if not maintenance_df.empty:

                st.dataframe(
                    maintenance_df,
                    use_container_width=True
                )

            else:

                st.info(
                    "No maintenance history"
                )



    st.stop()




   