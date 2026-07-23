
import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import(
    accuracy_score,
    classification_report,
    confusion_matrix
)

from app.ml.ai4i_dataset import load_ai4i_dataset

DATA_PATH = "../data/ai4i2020.csv"

def train_model():

    df = load_ai4i_dataset(DATA_PATH)

    X = df[
        [
            "Air temperature [K]",
            "Process temperature [K]",
            "Rotational speed [rpm]",
            "Torque [Nm]",
            "Tool wear [min]"
        ]
    ]


    y = df["Machine failure"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, 
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    print(
        "Accuracy:",
        accuracy_score(
            y_test,
            predictions
        )
    )


    print(
        classification_report(
            y_test,
            predictions
        )
    )


    print(
        confusion_matrix(
            y_test,
            predictions
        )
    )


    os.makedirs(
        "app/ml/saved_models",
        exist_ok=True
    )


    joblib.dump(
        model,
        "app/ml/saved_models/failure_model.pkl"
    )


    print("Model saved")


if __name__ == "__main__":
    train_model()