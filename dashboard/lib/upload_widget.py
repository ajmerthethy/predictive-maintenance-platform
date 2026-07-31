import io

import pandas as pd
import streamlit as st

from lib.api_client import upload_bulk_sensor_readings


def render_csv_upload_widget(machine_id, machine_name, key_prefix=""):
    """File-uploader + preview + submit for a single machine's historical
    sensor readings. Returns the number of rows inserted on a successful
    upload this run, else None (nothing uploaded yet, bad file, or a
    validation error already shown to the user).
    """

    uploaded_file = st.file_uploader(
        f"Sensor readings CSV for {machine_name}",
        type=["csv"],
        key=f"{key_prefix}_uploader_{machine_id}",
    )

    if uploaded_file is None:
        return None

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
        return None

    if not st.button("Upload", key=f"{key_prefix}_submit_{machine_id}"):
        return None

    status_code, payload = upload_bulk_sensor_readings(
        machine_id,
        uploaded_file.name,
        file_bytes,
    )

    if status_code == 200:
        st.success(
            f"Uploaded {payload['rows_inserted']} sensor readings "
            f"for {machine_name}."
        )
        return payload["rows_inserted"]

    detail = payload.get("detail") if payload else None

    if isinstance(detail, dict):

        st.error(detail.get("message", "Upload failed."))

        for row_error in detail.get("errors", []):
            st.write(f"- {row_error}")

    else:

        st.error(detail or "Upload failed. Please try again.")

    return None
