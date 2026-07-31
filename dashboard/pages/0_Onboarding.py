from datetime import date

import streamlit as st

from lib.api_client import (
    create_machine,
    get_machines,
    get_bulk_upload_template,
    get_prediction,
    get_health_score,
)
from lib.auth import require_login, logout_button
from lib.upload_widget import render_csv_upload_widget

st.set_page_config(
    page_title="Onboarding | Predictive Maintenance",
    page_icon="🏭",
    layout="wide"
)

require_login()
logout_button()

st.title("🚀 Customer Onboarding")

st.write(
    "Stand up a new pilot customer end to end: add their machines, "
    "backfill historical sensor data, and confirm health scores are "
    "showing before handing off to Fleet Overview."
)

if "onboarding_machines" not in st.session_state:
    st.session_state.onboarding_machines = []

if "onboarding_uploads" not in st.session_state:
    st.session_state.onboarding_uploads = {}


# -----------------------------
# STEP 1: ADD MACHINES
# -----------------------------

st.header("Step 1 - Add Machines")

with st.form("add_machine_form", clear_on_submit=True):

    col1, col2 = st.columns(2)

    with col1:
        name = st.text_input("Machine name*")
        manufacturer = st.text_input("Manufacturer")

    with col2:
        location = st.text_input("Location*")
        install_date = st.date_input(
            "Install date",
            value=None,
            max_value=date.today(),
        )

    submitted = st.form_submit_button("Add machine")

    if submitted:

        if not name or not location:
            st.error("Machine name and location are required.")

        else:
            created = create_machine(
                name=name,
                location=location,
                manufacturer=manufacturer or None,
                install_date=install_date,
            )

            if created:
                st.session_state.onboarding_machines.append(created)
                st.success(f"Added '{created['name']}'.")

            else:
                st.error("Could not add machine. Please try again.")

if st.session_state.onboarding_machines:

    st.write("Machines added this session:")

    st.dataframe(
        [
            {
                "Name": machine["name"],
                "Location": machine["location"],
                "Manufacturer": machine["manufacturer"] or "-",
            }
            for machine in st.session_state.onboarding_machines
        ]
    )

else:
    st.info("No machines added yet this session.")


# -----------------------------
# STEP 2: UPLOAD HISTORICAL DATA
# -----------------------------

st.divider()
st.header("Step 2 - Upload Historical Data")

all_machines = get_machines()

if not all_machines:

    st.info("Add at least one machine in Step 1 before uploading data.")

else:

    template_csv = get_bulk_upload_template()

    if template_csv:
        st.download_button(
            "⬇ Download CSV template",
            data=template_csv,
            file_name="sensor_readings_template.csv",
            mime="text/csv",
        )

    machine_lookup = {
        machine["id"]: machine["name"]
        for machine in all_machines
    }

    session_machine_ids = [
        machine["id"] for machine in st.session_state.onboarding_machines
    ]

    default_ids = session_machine_ids or list(machine_lookup.keys())

    selected_machine_id = st.selectbox(
        "Machine",
        options=list(machine_lookup.keys()),
        index=list(machine_lookup.keys()).index(default_ids[0]),
        format_func=lambda machine_id: machine_lookup[machine_id],
    )

    rows_inserted = render_csv_upload_widget(
        selected_machine_id,
        machine_lookup[selected_machine_id],
        key_prefix="onboarding",
    )

    if rows_inserted:

        st.session_state.onboarding_uploads[selected_machine_id] = (
            st.session_state.onboarding_uploads.get(selected_machine_id, 0)
            + rows_inserted
        )

        # Run one prediction against the latest uploaded reading so a
        # health score exists for the summary below - deliberately not
        # per historical row, just once after a backfill.
        get_prediction(selected_machine_id)


# -----------------------------
# STEP 3: SUMMARY
# -----------------------------

st.divider()
st.header("Step 3 - Summary")

if not st.session_state.onboarding_machines:

    st.info("Nothing to summarize yet - add a machine in Step 1 to begin.")

else:

    summary_rows = []

    for machine in st.session_state.onboarding_machines:

        machine_id = machine["id"]

        health = get_health_score(machine_id)

        summary_rows.append(
            {
                "Machine": machine["name"],
                "Readings Uploaded": st.session_state.onboarding_uploads.get(
                    machine_id, 0
                ),
                "Health Score": (
                    health["health_score"]
                    if health and "health_score" in health
                    else "Not yet available"
                ),
                "Rating": (
                    health["rating"]
                    if health and "rating" in health
                    else "-"
                ),
            }
        )

    st.dataframe(summary_rows)

    st.page_link(
        "streamlit_app.py",
        label="Go to Fleet Overview →",
        icon="🏭",
    )
