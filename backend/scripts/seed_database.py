import sys
import os

from dotenv import load_dotenv

load_dotenv()

sys.path.append(
    os.path.abspath("backend")
)

from app.db.database import SessionLocal
from app.models.machine import Machine
from app.models.sensor_reading import SensorReading
from app.models.prediction import Prediction
from app.models.alert import Alert
from app.models.maintenance import MaintenanceTask


db = SessionLocal()

def seed():

    print("Clearing existing data...")

    db.query(MaintenanceTask).delete()
    db.query(Alert).delete()
    db.query(Prediction).delete()
    db.query(SensorReading).delete()
    db.query(Machine).delete()

    db.commit()

    print("Creating machines...")

    machines = [
        Machine(
            name="CNC Machine 001",
            location="Factory Floor A",
            manufacturer="Mazak",
            install_date=date(2021,5,10),
            status="Healthy"
        ),

        Machine(
            name="Hydraulic Pump 001",
            location="Factory Floor B",
            manufacturer="Bosch Rexroth",
            install_date=date(2020,3,15),
            status="Healthy"
        ),

        Machine(
            name="Industrial Turbine 001",
            location="Power Room",
            manufacturer="Siemens",
            install_date=date(2019,8,20),
            status="Warning"
        ),

        Machine(
            name="Air Compressor 001",
            location="Utilities Room",
            manufacturer="Atlas Copco",
            install_date=date(2022,1,5),
            status="Healthy"
        ),

        Machine(
            name="Conveyor System 001",
            location="Assembly Line",
            manufacturer="Dorner",
            install_date=date(2023,6,12),
            status="Healthy"
        )
    ]

    db.add_all(machines)
    db.commit()

    for machine in machines:

        for i in range(20):

            reading = SensorReading(

                machine_id = machine.id,

                air_temperature=random.uniform(
                    295,305
                ),

                process_temperature=random.uniform(
                    305,320
                ),

                rotational_speed=random.uniform(
                    1200,1600
                ),

                torque=random.uniform(
                    30,60
                ),

                tool_wear=random.uniform(
                    10,200
                ),

                failure=False,

                timestamp=datetime.utcnow()
                -
                timedelta(
                    hours=i
                )

            )

            db.add(reading)

    db.commit()

    print("Creating predictions...")

    for machine in machines:

        probability = random.uniform(
            0.05,
            0.85
        )

        prediction = Prediction(
            machine_id = machine.id,

            prediction =
                1 if probability > 0.5 else 0,
            probability=probability
        )

        db.add(prediction)

    db.commit()

    print("Creating alerts...")

    alert = Alert(
        machine_id=3,

        severity="HIGH",

        message = 
        "Elevated temperature and torque detected",

        probability =0.82,

        recommended_action =
        "Inspect turbine cooling system",

        status = "OPEN"
    )

    db.add(alert)

    db.commit()

    print("Creating maintenance task...")

    task = MaintenanceTask(

        machine_id=3,

        alert_id=alert.id,

        description=
        "Inspect and service turbine cooling components",

        technician=
        "John Smith",

        status="OPEN",

        cost=4500
    )

    db.add(task)

    db.commit()

    print("Seed complete!")

if __name__ == "__main__":

    seed()

    