from sqlalchemy import Column, Integer, String, Date

from app.db.database import Base

class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    location = Column(String, nullable=False)

    manufacturer = Column(String)

    install_date = Column(Date)

    status = Column(String, default="Healthy")