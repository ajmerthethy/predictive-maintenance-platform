"""The one place that loads a versioned model artifact set and builds its
SHAP explainer. Every other module imports `model`/`explainer`/
`feature_importance`/`metadata`/`MODEL_VERSION` from here instead of reading
files itself.

Versioning is deliberately just files-on-disk, no registry service:

    saved_models/
        current_version.txt   <- e.g. "2" - the only mutable pointer
        v1/  failure_model.pkl  feature_importance.pkl  metadata.json
        v2/  failure_model.pkl  feature_importance.pkl  metadata.json

`current_version.txt` is read once, at import time (so a request never sees
two different versions mid-flight), and nothing is ever overwritten -
"rolling back" is editing that one file to point at an older vN/. See
train_ai4i.py for how a new version gets created and activated.
"""

import json
from pathlib import Path

import joblib
import shap

BASE_DIR = Path(__file__).resolve().parent

SAVED_MODELS_DIR = BASE_DIR / "saved_models"

CURRENT_VERSION_FILE = SAVED_MODELS_DIR / "current_version.txt"

MODEL_VERSION = CURRENT_VERSION_FILE.read_text().strip()

VERSION_DIR = SAVED_MODELS_DIR / f"v{MODEL_VERSION}"

MODEL_PATH = VERSION_DIR / "failure_model.pkl"
FEATURE_IMPORTANCE_PATH = VERSION_DIR / "feature_importance.pkl"
METADATA_PATH = VERSION_DIR / "metadata.json"

model = joblib.load(MODEL_PATH)

explainer = shap.TreeExplainer(model)

feature_importance = joblib.load(FEATURE_IMPORTANCE_PATH)

with open(METADATA_PATH) as _f:
    metadata = json.load(_f)


def resolve_version_dir(version):
    """The vN/ directory for an arbitrary version string, not just the
    currently active one - used by model_performance.py to look up
    metadata for predictions made by an older, since-replaced version.
    """

    return SAVED_MODELS_DIR / f"v{version}"


def load_metadata_for_version(version):
    """Best-effort metadata lookup for an arbitrary (possibly no-longer-
    active) version. Returns None if that version's files no longer exist.
    """

    path = resolve_version_dir(version) / "metadata.json"

    if not path.exists():
        return None

    with open(path) as f:
        return json.load(f)
