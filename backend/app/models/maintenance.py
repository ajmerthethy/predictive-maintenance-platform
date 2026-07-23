from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base


class MaintenanceTask(Base):

    __tablename__ = "maintenance_tasks"

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

    alert_id = Column(
        Integer,
        ForeignKey("alerts.id"),
        nullable=True
    )

    description = Column(
        String,
        nullable=False
    )

    technician = Column(
        String,
        nullable=True
    )

    status = Column(
        String,
        default="OPEN"
    )

    cost = Column(
        Float,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )

    machine = relationship(
        "Machine",
        back_populates="maintenance_tasks"
    )

    alert = relationship(
        "Alert",
        back_populates="maintenance_tasks"
    )

