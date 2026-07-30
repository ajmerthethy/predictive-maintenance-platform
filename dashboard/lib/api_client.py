import os

import requests

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000"
)


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

def get_machine_history(machine_id):

    response = requests.get(
        f"{API_URL}/history/machines/{machine_id}"
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
