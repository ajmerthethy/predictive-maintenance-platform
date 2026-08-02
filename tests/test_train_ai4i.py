import json
from datetime import datetime

import joblib
import pytest

from app.ml.train_ai4i import train_model, FEATURE_COLUMNS


def _write_synthetic_dataset(path):
    """A tiny synthetic stand-in for data/ai4i2020.csv - same columns
    train_model() actually reads, enough rows/both classes for a stratified
    80/20 split to succeed. Not meant to produce a good model, only to
    exercise the training + versioning pipeline quickly.
    """

    header = (
        "UDI,Product ID,Type,Air temperature [K],Process temperature [K],"
        "Rotational speed [rpm],Torque [Nm],Tool wear [min],Machine failure\n"
    )

    rows = []

    for i in range(16):
        rows.append(f"{i},P{i},M,298.{i},308.{i},1500,40,{i},0\n")

    for i in range(4):
        rows.append(f"{16 + i},F{i},M,310.{i},325.{i},1200,80,{200 + i},1\n")

    path.write_text(header + "".join(rows))


@pytest.fixture
def synthetic_data_path(tmp_path):
    path = tmp_path / "synthetic_ai4i.csv"
    _write_synthetic_dataset(path)
    return path


def test_train_model_creates_v1_with_all_three_artifacts(tmp_path, synthetic_data_path):
    output_dir = tmp_path / "saved_models"

    metadata = train_model(data_path=synthetic_data_path, output_dir=output_dir)

    assert metadata["version"] == 1

    version_dir = output_dir / "v1"
    assert (version_dir / "failure_model.pkl").exists()
    assert (version_dir / "feature_importance.pkl").exists()
    assert (version_dir / "metadata.json").exists()

    assert (output_dir / "current_version.txt").read_text().strip() == "1"

    with open(version_dir / "metadata.json") as f:
        persisted = json.load(f)
    assert persisted == metadata


def test_train_model_metadata_has_required_keys_and_sane_ranges(
    tmp_path, synthetic_data_path
):
    metadata = train_model(
        data_path=synthetic_data_path, output_dir=tmp_path / "saved_models"
    )

    for key in (
        "version",
        "trained_at",
        "algorithm",
        "framework",
        "sklearn_version",
        "hyperparameters",
        "feature_columns",
        "target",
        "metrics",
    ):
        assert key in metadata

    assert metadata["feature_columns"] == FEATURE_COLUMNS
    assert metadata["target"] == "Machine failure"

    metrics = metadata["metrics"]
    for key in ("accuracy", "precision", "recall", "f1_score"):
        assert 0.0 <= metrics[key] <= 1.0

    assert len(metrics["confusion_matrix"]) == 2
    assert all(len(row) == 2 for row in metrics["confusion_matrix"])
    assert metrics["n_train"] + metrics["n_test"] == 20


def test_train_model_trained_at_is_iso8601_utc(tmp_path, synthetic_data_path):
    metadata = train_model(
        data_path=synthetic_data_path, output_dir=tmp_path / "saved_models"
    )

    # Round-trips through datetime.fromisoformat without raising, and
    # carries explicit UTC offset information.
    parsed = datetime.fromisoformat(metadata["trained_at"])
    assert parsed.tzinfo is not None


def test_train_model_feature_importance_matches_feature_columns(
    tmp_path, synthetic_data_path
):
    output_dir = tmp_path / "saved_models"
    train_model(data_path=synthetic_data_path, output_dir=output_dir)

    feature_importance = joblib.load(output_dir / "v1" / "feature_importance.pkl")

    assert set(feature_importance["feature"]) == set(FEATURE_COLUMNS)
    # RandomForestClassifier.feature_importances_ always sums to ~1.
    assert feature_importance["importance"].sum() == pytest.approx(1.0, abs=1e-6)
    # Sorted descending by importance.
    assert list(feature_importance["importance"]) == sorted(
        feature_importance["importance"], reverse=True
    )


def test_train_model_second_run_creates_v2_without_touching_v1(
    tmp_path, synthetic_data_path
):
    output_dir = tmp_path / "saved_models"

    first = train_model(data_path=synthetic_data_path, output_dir=output_dir)
    v1_model_bytes = (output_dir / "v1" / "failure_model.pkl").read_bytes()

    second = train_model(data_path=synthetic_data_path, output_dir=output_dir)

    assert first["version"] == 1
    assert second["version"] == 2

    assert (output_dir / "v1" / "failure_model.pkl").exists()
    assert (output_dir / "v2" / "failure_model.pkl").exists()

    # v1's artifact is untouched by training v2.
    assert (output_dir / "v1" / "failure_model.pkl").read_bytes() == v1_model_bytes

    # The newest version is auto-activated.
    assert (output_dir / "current_version.txt").read_text().strip() == "2"


def test_train_model_activate_false_does_not_move_the_pointer(
    tmp_path, synthetic_data_path
):
    output_dir = tmp_path / "saved_models"

    train_model(data_path=synthetic_data_path, output_dir=output_dir)
    assert (output_dir / "current_version.txt").read_text().strip() == "1"

    train_model(
        data_path=synthetic_data_path, output_dir=output_dir, activate=False
    )

    # v2 was created on disk...
    assert (output_dir / "v2" / "failure_model.pkl").exists()
    # ...but the active pointer still says v1.
    assert (output_dir / "current_version.txt").read_text().strip() == "1"
