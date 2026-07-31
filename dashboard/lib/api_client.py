import os

import requests
import streamlit as st

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000"
)

# Off by default. Set SHOW_DEBUG_INFO=1 in a local/dev environment to see
# raw API payloads in the dashboard - never enable this in the pilot
# environment, it's not customer-appropriate.
SHOW_DEBUG_INFO = os.getenv("SHOW_DEBUG_INFO", "0") == "1"


def _auth_headers():
    token = st.session_state.get("auth_token")

    if token:
        return {"Authorization": f"Bearer {token}"}

    return {}


def _get(url, **kwargs):
    return requests.get(url, headers=_auth_headers(), **kwargs)


def _post(url, **kwargs):
    return requests.post(url, headers=_auth_headers(), **kwargs)


def _patch(url, **kwargs):
    return requests.patch(url, headers=_auth_headers(), **kwargs)


def acknowledge_alert(alert_id):

    response = _patch(
        f"{API_URL}/alerts/{alert_id}/acknowledge"
    )

    return response.status_code == 200


def resolve_alert(alert_id):

    response = _patch(
        f"{API_URL}/alerts/{alert_id}/resolve"
    )

    return response.status_code == 200

def get_explanation():

    response = _get(
        f"{API_URL}/prediction/explanation"
    )

    if response.status_code == 200:
        return response.json()

    return None

def get_machines():

    response = _get(
        f"{API_URL}/machines/"
    )

    if response.status_code == 200:
        return response.json()

    return []


def create_machine(
    name,
    location,
    manufacturer=None,
    install_date=None,
    status="active",
):

    payload = {
        "name": name,
        "location": location,
        "manufacturer": manufacturer,
        "status": status,
    }

    if install_date:
        payload["install_date"] = install_date.isoformat()

    response = _post(
        f"{API_URL}/machines/",
        json=payload,
    )

    if response.status_code == 200:
        return response.json()

    return None


def get_prediction(machine_id):

    response = _get(
        f"{API_URL}/prediction/machines/{machine_id}"
    )

    if response.status_code == 200:
        return response.json()

    return None

def get_maintenance_recommendation(machine_id):

    response = _get(
        f"{API_URL}/recommendations/machines/{machine_id}"
    )

    if response.status_code == 200:
        return response.json()

    return None



def get_sensor_readings(machine_id):

    response = _get(
        f"{API_URL}/sensor_readings/{machine_id}"
    )

    if response.status_code == 200:
        return response.json()

    return []

def get_alerts():

    response = _get(
        f"{API_URL}/alerts/"
    )

    if response.status_code == 200:
        return response.json()

    return []



def get_risk_ranking():

    response = _get(
        f"{API_URL}/analytics/machines/risk"
    )

    if response.status_code == 200:
        return response.json()

    return []

def get_analytics_summary():

    response = _get(
        f"{API_URL}/analytics/summary"
    )

    if response.status_code == 200:
        return response.json()

    return None


def get_maintenance_tasks():

    response = _get(
        f"{API_URL}/maintenance/"
    )

    if response.status_code == 200:
        return response.json()

    return []

def get_health_score(machine_id):

    response = _get(
        f"{API_URL}/health-score/machines/{machine_id}"
    )

    if response.status_code == 200:
        return response.json()

    return None

def get_downtime_cost(machine_id):

    response = _get(
        f"{API_URL}/downtime/machines/{machine_id}"
    )

    if response.status_code == 200:
        return response.json()

    return None

def get_maintenance_roi(machine_id):

    response = _get(
        f"{API_URL}/roi/machines/{machine_id}"
    )

    if response.status_code == 200:
        return response.json()

    return None

def create_maintenance_task(
    machine_id,
    description,
    technician=None,
    alert_id=None
):

    response = _post(
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

    response = _get(
        f"{API_URL}/alerts/?status=RESOLVED"
    )

    if response.status_code == 200:
        return response.json()

    return []

def get_machine_history(machine_id):

    response = _get(
        f"{API_URL}/history/machines/{machine_id}"
    )

    if response.status_code == 200:
        return response.json()

    return None

def get_machine_health(machine_id):

    response = _get(
        f"{API_URL}/machines/{machine_id}/health"
    )

    if response.status_code == 200:
        return response.json()

    return None

def get_executive_summary():

    response = _get(
        f"{API_URL}/executive/summary"
    )

    if response.status_code == 200:
        return response.json()

    return None

def get_maintenance_intelligence():

    response = _get(
        f"{API_URL}/maintenance-intelligence/summary"
    )

    if response.status_code == 200:
        return response.json()

    return None

def get_fleet_risk():

    response = _get(
        f"{API_URL}/fleet-risk/summary"
    )

    if response.status_code == 200:
        return response.json()

    return None


def get_bulk_upload_template():

    response = _get(
        f"{API_URL}/sensor_readings/bulk/template"
    )

    if response.status_code == 200:
        return response.content

    return None


def upload_bulk_sensor_readings(machine_id, filename, file_bytes):

    response = _post(
        f"{API_URL}/sensor_readings/bulk",
        params={"machine_id": machine_id},
        files={"file": (filename, file_bytes, "text/csv")},
    )

    try:
        payload = response.json()
    except ValueError:
        payload = None

    return response.status_code, payload
