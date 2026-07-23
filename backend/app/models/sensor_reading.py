
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base


class SensorReading(Base):

    __tablename__ = "sensor_readings"

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

    air_temperature = Column(
        Float,
        nullable=False
    )

    process_temperature = Column(
        Float,
        nullable=False
    )

    rotational_speed = Column(
        Float,
        nullable=False
    )

    torque = Column(
        Float,
        nullable=False
    )

    tool_wear = Column(
        Float,
        nullable=False
    )

    failure = Column(
        Boolean,
        default=False
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )


    machine = relationship(
        "Machine",
        back_populates="sensor_readings"
    )