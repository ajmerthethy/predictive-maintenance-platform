import sys
import os
import random

from datetime import datetime, timedelta, date

from dotenv import load_dotenv

load_dotenv()

# We are inside backend/scripts, so move up to backend
sys.path.append(
    os.path.abspath("..")
)

from app.db.database import SessionLocal

from app.models.account import Account
from app.models.machine import Machine
from app.models.sensor_reading import SensorReading
from app.models.prediction import Prediction
from app.models.alert import Alert
from app.models.maintenance import MaintenanceTask


DEFAULT_ACCOUNT_NAME = "Default Account"

db = SessionLocal()


def get_or_create_account(account_name):

    account = (
        db.query(Account)
        .filter(Account.name == account_name)
        .first()
    )

    if account:
        return account

    account = Account(name=account_name)
    db.add(account)
    db.commit()
    db.refresh(account)

    return account


def generate_sensor_data(profile, day):

    noise = lambda value: random.uniform(-value, value)

    if profile == "healthy":

        air_temperature = 298 + noise(2)

        process_temperature = 310 + noise(3)

        rotational_speed = 1500 + noise(75)

        torque = 45 + noise(5)

        tool_wear = 20 + (day * 0.15)


    elif profile == "aging":

        degradation = day / 90

        air_temperature = (
            300 +
            degradation * 10 +
            noise(2)
        )

        process_temperature = (
            315 +
            degradation * 15 +
            noise(3)
        )

        rotational_speed = (
            1500 -
            degradation * 100 +
            noise(50)
        )

        torque = (
            45 +
            degradation * 25 +
            noise(5)
        )

        tool_wear = (
            40 +
            degradation * 120
        )


    elif profile == "critical":

        degradation = day / 90

        air_temperature = (
            305 +
            degradation * 25 +
            noise(3)
        )

        process_temperature = (
            320 +
            degradation * 35 +
            noise(4)
        )

        rotational_speed = (
            1500 -
            degradation * 250 +
            noise(70)
        )

        torque = (
            55 +
            degradation * 40 +
            noise(8)
        )

        tool_wear = (
            70 +
            degradation * 130
        )


    return (
        air_temperature,
        process_temperature,
        rotational_speed,
        torque,
        min(tool_wear, 200)
    )


def calculate_probability(profile):

    if profile == "healthy":
        return random.uniform(0.02, 0.10)

    elif profile == "aging":
        return random.uniform(0.40, 0.65)

    elif profile == "critical":
        return random.uniform(0.80, 0.95)



def seed(account_name=DEFAULT_ACCOUNT_NAME):

    account = get_or_create_account(account_name)

    print(f"Clearing existing data for account '{account_name}'...")

    # Scoped to this account's machines only - this script must never
    # touch another customer's data, even accidentally, when re-seeding
    # one account's demo environment.
    account_machine_ids = (
        db.query(Machine.id)
        .filter(Machine.account_id == account.id)
        .subquery()
    )

    db.query(MaintenanceTask).filter(
        MaintenanceTask.machine_id.in_(account_machine_ids)
    ).delete(synchronize_session=False)

    db.query(Alert).filter(
        Alert.machine_id.in_(account_machine_ids)
    ).delete(synchronize_session=False)

    db.query(Prediction).filter(
        Prediction.machine_id.in_(account_machine_ids)
    ).delete(synchronize_session=False)

    db.query(SensorReading).filter(
        SensorReading.machine_id.in_(account_machine_ids)
    ).delete(synchronize_session=False)

    db.query(Machine).filter(
        Machine.account_id == account.id
    ).delete(synchronize_session=False)

    db.commit()


    print("Creating machines...")


    machine_configs = [

        (
            "CNC Machine 001",
            "Factory Floor A",
            "Mazak",
            "healthy"
        ),

        (
            "Hydraulic Pump 001",
            "Factory Floor B",
            "Bosch Rexroth",
            "aging"
        ),

        (
            "Industrial Turbine 001",
            "Power Room",
            "Siemens",
            "critical"
        ),

        (
            "Air Compressor 001",
            "Utilities Room",
            "Atlas Copco",
            "healthy"
        ),

        (
            "Conveyor System 001",
            "Assembly Line",
            "Dorner",
            "aging"
        )

    ]


    machines = []


    for name, location, manufacturer, profile in machine_configs:

        machine = Machine(

            name=name,

            location=location,

            manufacturer=manufacturer,

            install_date=date(2021, 1, 1),

            status="active",

            account_id=account.id,

        )

        db.add(machine)

        machines.append(
            (machine, profile)
        )


    db.commit()


    print("Generating sensor history...")


    now = datetime.utcnow()


    for machine, profile in machines:

        for day in range(90):

            for hour in range(24):

                (
                    air_temperature,
                    process_temperature,
                    rotational_speed,
                    torque,
                    tool_wear

                ) = generate_sensor_data(
                    profile,
                    day
                )


                reading = SensorReading(

                    machine_id=machine.id,

                    timestamp=(
                        now -
                        timedelta(
                            days=(90-day),
                            hours=hour
                        )
                    ),

                    air_temperature=air_temperature,

                    process_temperature=process_temperature,

                    rotational_speed=rotational_speed,

                    torque=torque,

                    tool_wear=tool_wear,

                    failure=False

                )

                db.add(reading)


    db.commit()


    print("Creating predictions...")


    for machine, profile in machines:

        probability = calculate_probability(profile)


        prediction = Prediction(

            machine_id=machine.id,

            prediction=(
                1
                if probability >= 0.5
                else 0
            ),

            probability=probability

        )

        db.add(prediction)


        if probability >= 0.70:

            alert = Alert(

                machine_id=machine.id,

                severity="HIGH",

                message=(
                    "Machine degradation detected. "
                    "Temperature, torque, and wear patterns "
                    "indicate elevated failure risk."
                ),

                probability=probability,

                recommended_action=(
                    "Schedule inspection and preventive "
                    "maintenance."
                ),

                status="OPEN"

            )


            db.add(alert)

            db.commit()


            task = MaintenanceTask(

                machine_id=machine.id,

                alert_id=alert.id,

                description=(
                    "Perform preventive maintenance "
                    "inspection and component evaluation."
                ),

                technician="Maintenance Team",

                status="OPEN",

                cost=random.uniform(
                    1000,
                    6000
                )

            )

            db.add(task)


    db.commit()


    print("Database seed complete!")


if __name__ == "__main__":

    account_name = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_ACCOUNT_NAME

    seed(account_name)
