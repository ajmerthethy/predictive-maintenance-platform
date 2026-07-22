from fastapi import FastAPI

from app.routers import machines
from app.routers import analytics
from app.routers import health
from app.routers import sensor_readings

from app.db.database import Base, engine
from app.models.machine import Machine
from app.models.sensor_reading import SensorReading


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Predictive Maintenance API",
    description="Backend API for Predictive Maintenance Platform",
    version="0.1.0"
)


app.include_router(machines.router)
app.include_router(health.router)
app.include_router(sensor_readings.router)
app.include_router(analytics.router)

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

