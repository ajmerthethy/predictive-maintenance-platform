
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base
from sqlalchemy import Boolean

class SensorReading(Base):
    __tablename__ = "sensor_readings"

    id = Column(Integer, primary_key=True, index=True)

    machine_id = Column(
        Integer, 
        ForeignKey("machines.id"),
        nullable = False
    )

    temperature = Column(Float, nullable=False)

    vibration = Column(Float, nullable=False)

    pressure = Column(Float, nullable=False)

    timestamp = Column(
        DateTime,
        default=datetime.utcnow
    )

    machine = relationship(
        "Machine",
        back_populates="sensor_readings"
    )

    failure = Column(Boolean, default=False)

    