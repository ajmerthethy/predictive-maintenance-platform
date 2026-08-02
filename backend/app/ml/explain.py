from app.ml.model_loader import feature_importance


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
