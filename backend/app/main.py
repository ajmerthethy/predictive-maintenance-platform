from fastapi import FastAPI

from app.db.database import Base, engine
from app.models.machine import Machine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Predictive Maintenance API",
    description="Backend API for Predictive Maintenance Platform",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "message": "Welcome to the Predictive Maintenance Platform API!"

    }
@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }

