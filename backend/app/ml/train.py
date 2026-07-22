import os
import joblib
import pandas as pd


from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)

from app.models.machine import Machine
from app.models.sensor_reading import SensorReading
from app.models.prediction import Prediction

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
        X,
        y,
        test_size=0.2,
        random_state=42
    )


    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )


    model.fit(
        X_train,
        y_train
    )


    # -----------------------------
    # Feature Importance
    # -----------------------------

    feature_importance = pd.DataFrame(
        {
            "feature": X.columns,
            "importance": model.feature_importances_
        }
    )


    feature_importance = feature_importance.sort_values(
        by="importance",
        ascending=False
    )


    print("\nFeature Importance:")
    print(feature_importance)


    # Save feature importance

    model_dir = "app/ml/saved_models"

    os.makedirs(
        model_dir,
        exist_ok=True
    )


    importance_path = os.path.join(
        model_dir,
        "feature_importance.pkl"
    )


    joblib.dump(
        feature_importance,
        importance_path
    )


    print(
        f"Feature importance saved to: {importance_path}"
    )


    # -----------------------------
    # Model Evaluation
    # -----------------------------

    predictions = model.predict(
        X_test
    )


    accuracy = accuracy_score(
        y_test,
        predictions
    )


    print(
        f"Model accuracy: {accuracy:.2f}"
    )


    print(
        "\nClassification Report:"
    )

    print(
        classification_report(
            y_test,
            predictions
        )
    )


    print(
        "\nConfusion Matrix:"
    )

    print(
        confusion_matrix(
            y_test,
            predictions
        )
    )


    # -----------------------------
    # Save Model
    # -----------------------------

    model_path = os.path.join(
        model_dir,
        "failure_model.pkl"
    )


    joblib.dump(
        model,
        model_path
    )


    print(
        f"Model saved to: {model_path}"
    )


    db.close()


    return model



if __name__ == "__main__":

    train_model()