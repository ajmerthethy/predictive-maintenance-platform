import streamlit as st

from lib.api_client import get_machines, get_bulk_upload_template
from lib.auth import require_login, logout_button
from lib.upload_widget import render_csv_upload_widget

st.set_page_config(
    page_title="Upload Data | Predictive Maintenance",
    page_icon="🏭",
    layout="wide"
)

require_login()
logout_button()

st.header("📤 Upload Historical Sensor Data")

st.write(
    "Upload a CSV export of historical sensor readings for a machine - "
    "this is the fastest way to backfill a machine's history during "
    "onboarding, instead of entering readings one at a time."
)

template_csv = get_bulk_upload_template()

if template_csv:
    st.download_button(
        "⬇ Download CSV template",
        data=template_csv,
        file_name="sensor_readings_template.csv",
        mime="text/csv",
    )

machines = get_machines()

if not machines:
    st.info(
        "No machines found. Add a machine before uploading sensor data."
    )
    st.stop()

machine_lookup = {
    machine["id"]: machine["name"]
    for machine in machines
}

selected_machine_id = st.selectbox(
    "Machine",
    options=list(machine_lookup.keys()),
    format_func=lambda machine_id: machine_lookup[machine_id],
)

render_csv_upload_widget(
    selected_machine_id,
    machine_lookup[selected_machine_id],
    key_prefix="upload_page",
)
