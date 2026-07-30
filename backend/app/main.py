from fastapi import FastAPI

from app.routers import machines
from app.routers import analytics
from app.routers import health
from app.routers import sensor_readings
from app.routers import prediction
from app.routers import downtime
from app.routers.auth import router as auth_router
from app.routers import alerts
from app.routers import maintenance
from app.routers import maintenance_summary
from app.routers import history
from app.routers import recommendations
from app.routers import health_score
from app.routers import maintenance_roi
from app.routers import executive
from app.routers import fleet_risk
from app.routers import maintenance_intelligence


app = FastAPI(
    title="Predictive Maintenance API",
    description="Backend API for Predictive Maintenance Platform",
    version="0.1.0"
)


app.include_router(machines.router)
app.include_router(health.router)
app.include_router(sensor_readings.router)
app.include_router(analytics.router)
app.include_router(prediction.router)
app.include_router(alerts.router)
app.include_router(auth_router)
app.include_router(maintenance.router)
app.include_router(maintenance_summary.router)
app.include_router(history.router)
app.include_router(recommendations.router)
app.include_router(health_score.router)
app.include_router(downtime.router)
app.include_router(maintenance_roi.router)
app.include_router(executive.router)
app.include_router(fleet_risk.router)
app.include_router(maintenance_intelligence.router)

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
