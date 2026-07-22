
import random
import time
from datetime import datetime

import requests

API_URL = "http://127.0.0.1:8000/sensor_readings/"


machine_id = 1

for i in range(50):

    # simulate gradual degradation
    degradation = i * 0.15

    temperature = random.uniform(65, 75) + degradation

    vibration = random.uniform(1, 2) + degradation / 5

    pressure = random.uniform(100, 120) - degradation

    payload = {
        "machine_id": machine_id,
        "temperature": round(temperature, 2),
        "vibration": round(vibration, 2),
        "pressure": round(pressure, 2),
        "timestamp": datetime.utcnow().isoformat()
    }

    response = requests.post(API_URL, json=payload)

    print(
        f"Reading {i+1}:",
        response.status_code,
        payload
    )


    time.sleep(1)