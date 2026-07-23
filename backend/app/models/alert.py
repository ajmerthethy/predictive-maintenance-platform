
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base


class Alert(Base):

    __tablename__ = "alerts"

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

    severity = Column(
        String,
        nullable=False
    )

    message = Column(
        String,
        nullable=False
    )

    probability = Column(
        Float,
        nullable=False
    )

    recommended_action = Column(
        String,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


    machine = relationship(
        "Machine",
        back_populates="alerts"
    )

    status = Column(
    String,
    nullable=False,
    default="OPEN"
    )

    resolved_at = Column(
        DateTime,
        nullable=True
    )