
import random
import time
from datetime import datetime, timedelta

import requests


API_URL = "http://127.0.0.1:8000/sensor_readings/"


NUM_MACHINES = 10
READINGS_PER_MACHINE = 500


start_time = datetime.utcnow()


for machine_id in range(1, NUM_MACHINES + 1):

    # Different machines degrade differently
    degradation_rate = random.uniform(0.01, 0.03)

    # Random point where machine starts failing
    failure_threshold = random.uniform(12, 18)

    print(f"\nGenerating data for Machine {machine_id}")

    for i in range(READINGS_PER_MACHINE):

        # gradual degradation
        degradation = i * degradation_rate


        # Sensor noise
        temperature_noise = random.uniform(-2, 2)
        vibration_noise = random.uniform(-0.15, 0.15)
        pressure_noise = random.uniform(-3, 3)


        temperature = (
            random.uniform(65, 75)
            + degradation
            + temperature_noise
        )


        vibration = (
            random.uniform(1, 2)
            + (degradation / 6)
            + vibration_noise
        )


        pressure = (
            random.uniform(100, 120)
            - degradation
            + pressure_noise
        )


        # More realistic failure generation
        failure_probability = 0

        if degradation > failure_threshold:
            failure_probability = 0.7

        elif degradation > failure_threshold * 0.7:
            failure_probability = 0.25

        else:
            failure_probability = 0.02


        failure = random.random() < failure_probability


        payload = {
            "machine_id": machine_id,
            "failure": int(failure),
            "temperature": round(temperature, 2),
            "vibration": round(vibration, 2),
            "pressure": round(pressure, 2),
            "timestamp": (
                start_time + timedelta(minutes=i)
            ).isoformat()
        }


        response = requests.post(
            API_URL,
            json=payload
        )


        if i % 50 == 0:
            print(
                f"Reading {i}/{READINGS_PER_MACHINE}",
                response.status_code
            )


        time.sleep(0.01)


print("\nSensor data generation complete.")