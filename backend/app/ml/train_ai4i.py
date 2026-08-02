import json
import re
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
import sklearn

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from app.ml.ai4i_dataset import load_ai4i_dataset

# Resolved from this file's own location rather than the caller's working
# directory - the previous "../data/ai4i2020.csv" only worked when the
# script happened to be run from backend/app/ml/, and silently
# FileNotFoundError'd from anywhere else.
BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parents[2]

DEFAULT_DATA_PATH = REPO_ROOT / "data" / "ai4i2020.csv"

# The saved_models ROOT, not a specific version - train_model() creates a
# new vN/ subdirectory under this on every call (see _next_version below)
# and, by default, activates it. Nothing under here is ever overwritten;
# "rolling back" to an older model is just editing current_version.txt.
DEFAULT_OUTPUT_DIR = BASE_DIR / "saved_models"

MODEL_FILENAME = "failure_model.pkl"
FEATURE_IMPORTANCE_FILENAME = "feature_importance.pkl"
METADATA_FILENAME = "metadata.json"
CURRENT_VERSION_FILENAME = "current_version.txt"

FEATURE_COLUMNS = [
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
]

TARGET_COLUMN = "Machine failure"

_VERSION_DIR_PATTERN = re.compile(r"^v(\d+)$")


def _next_version(output_dir):
    """1 if output_dir has no vN/ subdirectories yet, otherwise the
    highest existing version + 1. Versions are never reused or
    overwritten.
    """

    existing = [
        int(match.group(1))
        for path in Path(output_dir).glob("v*")
        if path.is_dir()
        for match in [_VERSION_DIR_PATTERN.match(path.name)]
        if match
    ]

    return max(existing, default=0) + 1


def train_model(data_path=DEFAULT_DATA_PATH, output_dir=DEFAULT_OUTPUT_DIR, activate=True):
    """Trains a fresh model, writes it (plus auto-generated feature
    importance and metadata) into a new, never-before-used vN/ directory
    under `output_dir`, and - unless `activate=False` - points
    current_version.txt at it so the running app picks it up on next
    restart. Returns the full metadata dict, including `version`.
    """

    df = load_ai4i_dataset(data_path)

    X = df[FEATURE_COLUMNS]

    y = df[TARGET_COLUMN]

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

    # Cast explicitly to native Python types - sklearn's metric functions
    # return numpy scalars, which json.dump cannot always be trusted to
    # serialize.
    accuracy = float(accuracy_score(y_test, predictions))
    precision = float(precision_score(y_test, predictions, zero_division=0))
    recall = float(recall_score(y_test, predictions, zero_division=0))
    f1 = float(f1_score(y_test, predictions, zero_division=0))
    matrix = confusion_matrix(y_test, predictions)

    print("Accuracy:", accuracy)
    print(classification_report(y_test, predictions))
    print(matrix)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    version = _next_version(output_dir)
    version_dir = output_dir / f"v{version}"
    version_dir.mkdir(parents=True, exist_ok=False)

    joblib.dump(model, version_dir / MODEL_FILENAME)

    # Auto-generated from this exact model - previously a hand-maintained,
    # separately-committed file that had no code path regenerating it and
    # had silently drifted to describe a completely different (pre-AI4I)
    # feature set. Tying it to the model that produced it means it can
    # never go stale again.
    feature_importance_df = (
        pd.DataFrame(
            {
                "feature": FEATURE_COLUMNS,
                "importance": model.feature_importances_,
            }
        )
        .sort_values("importance", ascending=False)
        .reset_index(drop=True)
    )

    joblib.dump(
        feature_importance_df,
        version_dir / FEATURE_IMPORTANCE_FILENAME,
    )

    # Persisted alongside the model artifact so "what accuracy/recall does
    # the currently-deployed model achieve, and what was it trained with"
    # has an answer that doesn't require retraining (or reading git
    # history) to find out.
    metadata = {
        "version": version,
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "algorithm": "RandomForestClassifier",
        "framework": "scikit-learn",
        "sklearn_version": sklearn.__version__,
        "hyperparameters": model.get_params(),
        "feature_columns": FEATURE_COLUMNS,
        "target": TARGET_COLUMN,
        "metrics": {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "confusion_matrix": matrix.tolist(),
            "n_train": len(X_train),
            "n_test": len(X_test),
        },
        "notes": None,
    }

    metadata_path = version_dir / METADATA_FILENAME

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    if activate:
        (output_dir / CURRENT_VERSION_FILENAME).write_text(f"{version}\n")

    print(f"Model saved as version {version} in {version_dir}")
    print(f"Metadata saved to {metadata_path}")
    if activate:
        print(f"current_version.txt now points at v{version}")

    return metadata


if __name__ == "__main__":
    train_model()
