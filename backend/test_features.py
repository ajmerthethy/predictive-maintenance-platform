
from app.db.database import SessionLocal
from app.ml.dataset import create_training_dataset
from app.ml.features import create_ml_features

db = SessionLocal()

df = create_training_dataset(db)

features = create_ml_features(df)

print(features)

db.close()