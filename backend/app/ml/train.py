import os
import joblib



from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

from app.models.machine import Machine
from app.models.sensor_reading import SensorReading

from app.db.database import SessionLocal
from app.ml.dataset import create_training_dataset

def train_model():
    db = SessionLocal()

    df = create_training_dataset(db)

    X = df[
        [
            "temperature",
            "vibration",
            "pressure"
        ]
    ]

    y = df["failure"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)

    print(f"Model accuracy: {accuracy:.2f}")

        # Save trained model
    model_dir = "app/ml/saved_models"

    os.makedirs(model_dir, exist_ok=True)

    model_path = os.path.join(
        model_dir,
        "failure_model.pkl"
    )

    joblib.dump(model, model_path)

    print(f"Model saved to: {model_path}")

    db.close()

    return model

if __name__ == "__main__":
    train_model()