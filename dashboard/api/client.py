
import requests

BASE_URL = "http://127.0.0.1:8000"

def get_machines():

    response = requests.get(
        f"{BASE_URL}/machines/"

    )

    response.raise_for_status()

    return response.json()


def get_alerts():

    response = requests.get(
        f"{BASE_URL}/alerts/"

    )

    response.raise_for_status()

    return response.json()

def get_maintenance():

    response = requests.get(
        f"{BASE_URL}/maintenance/"

    )

    response.raise_for_status()

    return response.json()