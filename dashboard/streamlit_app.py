import streamlit as st
import pandas as pd
import plotly.express as px

from lib.api_client import (
    get_risk_ranking,
    get_maintenance_intelligence,
    get_analytics_summary,
)
from lib.auth import require_login, logout_button
from lib.business_rules import calculate_fleet_status

st.set_page_config(
    page_title="Fleet Overview | Predictive Maintenance",
    page_icon="🏭",
    layout="wide"
)

require_login()
logout_button()

st.title("🏭 Predictive Maintenance Dashboard")


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
{"Immediate inspection required" if highest["risk_level"] == "CRITICAL" else "Inspect within 7 days"}
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

    # Calculate health score
    risk_df["health_score"] = (
        100 - risk_df["failure_probability"]
    ).round(1)

    # Generate recommendations
    def get_risk_action(risk_level):

        if risk_level == "CRITICAL":
            return "🔴 Immediate inspection required"

        elif risk_level == "WARNING":
            return "🟡 Inspect within 7 days"

        else:
            return "🟢 Continue monitoring"

    risk_df["recommended_action"] = (
        risk_df["risk_level"]
        .apply(get_risk_action)
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

    risk_bar = px.bar(
        risk_df,
        x="Machine",
        y="Failure Risk (%)",
        color="Risk Level",
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

    fleet_health = risk_df["Health Score"].mean()

    st.metric(
        "Fleet Health Score",
        f"{fleet_health:.1f}/100"
    )

else:

    st.info(
        "No machines with predictions yet. Add a machine and upload "
        "some sensor data to see your fleet overview here."
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


        if machine["risk_level"] == "CRITICAL":

            critical_machines.append(machine_info)

        elif machine["risk_level"] == "WARNING":

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
        "No machines with predictions yet. Add a machine and upload "
        "some sensor data to see your fleet overview here."
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

    st.info(
        "No prediction data yet. This section fills in once machines "
        "have sensor readings and at least one prediction has run."
    )
