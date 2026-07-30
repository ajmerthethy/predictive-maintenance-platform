import streamlit as st
import pandas as pd

from lib.api_client import get_executive_summary, get_fleet_risk

st.set_page_config(
    page_title="Predictive Maintenance Dashboard",
    layout="wide"
)

st.header(
    "📊 Executive Dashboard"
)

data = get_executive_summary()

if not data:
    st.error(
        "Executive analytics unavailable"
    )
    st.stop()


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
