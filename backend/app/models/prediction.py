from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
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

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    machine = relationship(
        "Machine",
        back_populates="predictions"
    )