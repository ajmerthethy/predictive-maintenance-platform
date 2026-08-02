from app.ml import model_loader, predict


def test_predict_module_reuses_the_single_shared_model_instance():
    """predict.py must not load its own copy of the model file - it should
    be the exact same object model_loader loaded once at import time (see
    ML/MLOps audit, Immediate #6: previously live_prediction.py loaded a
    second, unused copy).
    """
    assert predict.model is model_loader.model
    assert predict.explainer is model_loader.explainer


def test_live_prediction_module_does_not_load_its_own_model_copy():
    """live_prediction.py previously did its own joblib.load(...) into a
    module-level `model` name that was never used. It shouldn't exist at
    all now.
    """
    from app.ml import live_prediction

    assert not hasattr(live_prediction, "model")


# -----------------------------
# VERSIONING (ML/MLOps audit, Near-Term #1/#2)
# -----------------------------

def test_model_loader_exposes_a_version_matching_current_version_txt():
    on_disk = (model_loader.SAVED_MODELS_DIR / "current_version.txt").read_text().strip()
    assert model_loader.MODEL_VERSION == on_disk


def test_model_loader_metadata_version_matches_module_level_version():
    assert str(model_loader.metadata["version"]) == model_loader.MODEL_VERSION


def test_model_loader_feature_importance_is_not_stale():
    """Regression test for a real bug found while implementing this:
    v1's feature_importance.pkl used to list 'vibration'/'temperature'/
    'pressure' - features from an earlier, pre-AI4I iteration of this
    project - rather than the 5 features this model actually uses. It must
    now match the model's real feature names.
    """
    assert set(model_loader.feature_importance["feature"]) == set(
        model_loader.metadata["feature_columns"]
    )


def test_resolve_version_dir_points_at_the_versioned_folder():
    assert model_loader.resolve_version_dir("1").name == "v1"


def test_load_metadata_for_version_returns_none_for_a_nonexistent_version():
    assert model_loader.load_metadata_for_version("9999") is None


def test_load_metadata_for_version_returns_metadata_for_the_active_version():
    metadata = model_loader.load_metadata_for_version(model_loader.MODEL_VERSION)
    assert metadata == model_loader.metadata
