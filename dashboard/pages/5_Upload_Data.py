import io

import pandas as pd
import streamlit as st

from lib.api_client import (
    get_machines,
    get_bulk_upload_template,
    upload_bulk_sensor_readings,
)
from lib.auth import require_login, logout_button

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

uploaded_file = st.file_uploader(
    "Sensor readings CSV",
    type=["csv"],
)

if uploaded_file is not None:

    file_bytes = uploaded_file.getvalue()

    try:
        preview_df = pd.read_csv(io.BytesIO(file_bytes))
        st.write(f"Preview (first 5 of {len(preview_df)} rows):")
        st.dataframe(preview_df.head())

    except Exception:
        st.error(
            "Could not read this file as a CSV - check the format "
            "and try again."
        )
        st.stop()

    if st.button("Upload"):

        status_code, payload = upload_bulk_sensor_readings(
            selected_machine_id,
            uploaded_file.name,
            file_bytes,
        )

        if status_code == 200:

            st.success(
                f"Uploaded {payload['rows_inserted']} sensor readings "
                f"for {machine_lookup[selected_machine_id]}."
            )

        else:

            detail = payload.get("detail") if payload else None

            if isinstance(detail, dict):

                st.error(detail.get("message", "Upload failed."))

                for row_error in detail.get("errors", []):
                    st.write(f"- {row_error}")

            else:

                st.error(detail or "Upload failed. Please try again.")
