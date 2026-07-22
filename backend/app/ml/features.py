import pandas as pd


def create_ml_features(df):

    features = {}

    features["temperature_mean"] = df["temperature"].mean()
    features["temperature_std"] = df["temperature"].std()
    features["temperature_change"] = (
        df["temperature"].iloc[-1] -
        df["temperature"].iloc[0]
    )

    features["vibration_mean"] = df["vibration"].mean()
    features["vibration_std"] = df["vibration"].std()
    features["vibration_change"] = (
        df["vibration"].iloc[-1] -
        df["vibration"].iloc[0]
    )

    features["pressure_mean"] = df["pressure"].mean()
    features["pressure_change"] = (
        df["pressure"].iloc[-1] -
        df["pressure"].iloc[0]
    )

    return pd.DataFrame([features])