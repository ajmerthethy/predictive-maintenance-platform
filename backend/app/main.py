import logging

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import (
    JWT_SECRET_KEY,
    validate_jwt_secret_key,
    check_resend_sender_configured,
)
from app.core.logging_config import configure_logging
from app.core.security import get_current_user
from app.db.database import get_db
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

# Fail fast rather than boot with a forgeable auth secret.
validate_jwt_secret_key(JWT_SECRET_KEY)

# Non-fatal - just makes a misconfigured email sender visible in the
# deploy logs immediately, instead of only discovered when an alert
# silently never reaches its recipient.
check_resend_sender_configured()

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
    """Pure liveness check - always 200 if the process can respond at
    all, with zero dependency on the database. This is what local
    docker-compose's own healthcheck targets; keep it that way, since a
    container-restart policy tied to DB reachability can cause exactly
    the kind of restart loop this endpoint is meant to avoid. Point an
    external uptime monitor at /health/db below instead, which actually
    catches "the process is up but can't reach the database."
    """
    return {
        "status": "healthy"
    }


@app.get("/health/db")
def health_check_db(db: Session = Depends(get_db)):
    """Readiness check: confirms the database is actually reachable, not
    just that the process is running. Unauthenticated, like /health -
    an external uptime monitor won't have a bearer token.
    """
    try:
        db.execute(text("SELECT 1"))

    except Exception:
        logger.exception("Database health check failed")
        raise HTTPException(
            status_code=503,
            detail="Database unavailable",
        )

    return {
        "status": "healthy",
        "database": "reachable",
    }
