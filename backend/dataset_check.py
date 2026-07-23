
from app.db.database import SessionLocal
from app.models.machine import Machine
from app.models.sensor_reading import SensorReading
from app.ml.dataset import create_training_dataset


db = SessionLocal()

df = create_training_dataset(db)

print(df.head())
print("\nDataset shape:")
print(df.shape)

db.close()