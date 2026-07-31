import logging

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.logging_config import configure_logging
from app.core.security import get_current_user
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

configure_logging()
logger = logging.getLogger(__name__)


app = FastAPI(
    title="Predictive Maintenance API",
    description="Backend API for Predictive Maintenance Platform",
    version="0.1.0"
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "Unhandled exception while processing %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# /auth and the root-level GET /health liveness check (defined at the
# bottom of this file) are the only unauthenticated routes. health.router
# is a different thing despite the name - it serves real per-machine data
# (GET /machines/{id}/health, /trend) and requires a login like everything
# else. It was previously registered without auth by mistake, exempted
# alongside the liveness check on the assumption they were the same route.
_auth = [Depends(get_current_user)]

app.include_router(auth_router)

app.include_router(health.router, dependencies=_auth)
app.include_router(machines.router, dependencies=_auth)
app.include_router(sensor_readings.router, dependencies=_auth)
app.include_router(analytics.router, dependencies=_auth)
app.include_router(prediction.router, dependencies=_auth)
app.include_router(alerts.router, dependencies=_auth)
app.include_router(maintenance.router, dependencies=_auth)
app.include_router(maintenance_summary.router, dependencies=_auth)
app.include_router(history.router, dependencies=_auth)
app.include_router(recommendations.router, dependencies=_auth)
app.include_router(health_score.router, dependencies=_auth)
app.include_router(downtime.router, dependencies=_auth)
app.include_router(maintenance_roi.router, dependencies=_auth)
app.include_router(executive.router, dependencies=_auth)
app.include_router(fleet_risk.router, dependencies=_auth)
app.include_router(maintenance_intelligence.router, dependencies=_auth)

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
