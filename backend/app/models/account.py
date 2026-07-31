from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.db.database import Base


class Account(Base):
    """A customer/tenant. Every User and every Machine belongs to exactly
    one Account - this is the isolation boundary. Multiple users can
    share an Account (e.g. several staff at the same pilot customer all
    need to see the same fleet), but no query should ever cross accounts.
    """

    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, unique=True, nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    users = relationship("User", back_populates="account")

    machines = relationship("Machine", back_populates="account")
