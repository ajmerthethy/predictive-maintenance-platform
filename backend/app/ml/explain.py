
import joblib
import os

IMPORTANCE_PATH = os.path.join(
    "app",
    "ml",
    "saved_models",
    "feature_importance.pkl"
)

feature_importance = joblib.load(
    IMPORTANCE_PATH
)

def get_feature_importance():

    results = []

    for _, row in feature_importance.iterrows():

        results.append(
            {
                "feature": row["feature"],
                "importance": float(
                    row["importance"]
                )
            }
        )

    return results