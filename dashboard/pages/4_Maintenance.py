import streamlit as st
import pandas as pd
import requests

from lib.api_client import API_URL, get_machines, get_maintenance_tasks

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
