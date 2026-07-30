import streamlit as st
import pandas as pd

from lib.api_client import (
    get_machines,
    get_alerts,
    get_alert_history,
    acknowledge_alert,
    resolve_alert,
    create_maintenance_task,
)

st.set_page_config(
    page_title="Predictive Maintenance Dashboard",
    layout="wide"
)

machines = get_machines()

machine_lookup = {
    machine["id"]: machine
    for machine in machines
}

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
