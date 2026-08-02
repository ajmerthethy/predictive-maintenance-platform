from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, JSON, String
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base


class Prediction(Base):

    __tablename__ = "predictions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    machine_id = Column(
        Integer,
        ForeignKey("machines.id"),
        nullable=False
    )

    prediction = Column(
        Integer,
        nullable=False
    )

    probability = Column(
        Float,
        nullable=False
    )

    # Nullable: only populated when this prediction was computed from a
    # stored SensorReading (see app/ml/live_prediction.py). POST /prediction/
    # takes raw values straight from the request body, with no reading to
    # link back to.
    sensor_reading_id = Column(
        Integer,
        ForeignKey("sensor_readings.id"),
        nullable=True
    )

    # The SHAP explanation computed at prediction time, persisted so a GET
    # can return it later without re-running inference (see
    # app/routers/prediction.py::predict_latest).
    top_factors = Column(
        JSON,
        nullable=True
    )

    # The exact 5 feature values fed to the model for this prediction -
    # independent of sensor_reading_id, which may be null (POST /prediction/
    # takes raw values with no backing reading) or could point at a reading
    # since edited/deleted. Makes every prediction reproducible on its own.
    input_features = Column(
        JSON,
        nullable=True
    )

    # Which saved_models/vN/ produced this prediction (see
    # app/ml/model_loader.py). Nullable - predictions made before model
    # versioning existed have no recorded version.
    model_version = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    machine = relationship(
        "Machine",
        back_populates="predictions"
    )

    sensor_reading = relationship(
        "SensorReading"
    )