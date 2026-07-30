import os
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

REPO_ROOT = Path(__file__).resolve().parent.parent

# Every module under backend/app/ uses absolute imports like
# `from app.models.machine import Machine`, which only resolve correctly
# with backend/ on sys.path (pytest.ini's `pythonpath = backend`) - so
# `app.*` is the only import path backend/app/main.py itself can use
# internally. Importing it here as `backend.app.main` instead (as the test
# files originally did) creates a SECOND, distinct copy of every module
# under a different sys.modules key: a different `app` FastAPI instance and
# a different `get_db` function object, so overriding dependencies on it
# silently does nothing to the app the tests actually exercise. Confirmed by
# direct comparison (`app.main.app is not backend.app.main.app`) while
# debugging why rollback appeared to not work. Every test file's import was
# changed to match this (`from app.main import app`) for the same reason.
from app.main import app
from app.db.database import get_db
from app.models.machine import Machine
from app.models.alert import Alert
from app.models.maintenance import MaintenanceTask


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise RuntimeError(
        "TEST_DATABASE_URL is not set. The test suite creates/rolls back "
        "real rows and must never run against DATABASE_URL (which may point "
        "at a real database) without an explicit, separate opt-in. Point it "
        "at a disposable Postgres instance, e.g.:\n"
        "  TEST_DATABASE_URL=postgresql://ci_user:ci_password@localhost:5433/ci_test_db"
    )

_engine = create_engine(TEST_DATABASE_URL)


@pytest.fixture(scope="session", autouse=True)
def _migrated_test_database():
    """Bring the disposable test database to the current Alembic head, once
    per test session. Runs in a subprocess (rather than in-process via
    alembic.command) so it always re-reads DATABASE_URL fresh, regardless of
    what this pytest process may have already imported/cached.
    """
    env = {**os.environ, "DATABASE_URL": TEST_DATABASE_URL}
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=str(REPO_ROOT),
        env=env,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            "Failed to migrate the test database to head:\n"
            f"--- stdout ---\n{result.stdout}\n"
            f"--- stderr ---\n{result.stderr}"
        )


@pytest.fixture(autouse=True)
def db_session(_migrated_test_database):
    """Isolate each test in its own rolled-back transaction.

    App code calls db.commit() internally (e.g. routers/prediction.py,
    services), which would normally end an outer transaction early.
    join_transaction_mode="create_savepoint" (SQLAlchemy 2.0+) makes the
    session run every transaction as a SAVEPOINT and automatically start a
    new one after each commit, so application code can commit freely while
    the outermost transaction - and everything written under it - is still
    rolled back when the test ends. Verified empirically: an app-level
    commit() followed by rolling back the outer transaction leaves zero
    rows behind, checked from a separate connection.
    """
    connection = _engine.connect()
    outer_transaction = connection.begin()

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=connection,
        join_transaction_mode="create_savepoint",
    )
    session = TestingSessionLocal()

    def _override_get_db():
        yield session

    app.dependency_overrides[get_db] = _override_get_db

    yield session

    app.dependency_overrides.pop(get_db, None)
    session.close()
    outer_transaction.rollback()
    connection.close()


@pytest.fixture()
def machine(db_session):
    """A Machine row tests can depend on instead of assuming any particular
    id (e.g. `machine_id=1`) already exists.
    """
    db_machine = Machine(
        name="Test Machine",
        location="Test Location",
        manufacturer="Test Manufacturer",
        status="Healthy",
    )
    db_session.add(db_machine)
    db_session.commit()
    db_session.refresh(db_machine)
    return db_machine


@pytest.fixture()
def alert(db_session, machine):
    """An Alert row tied to `machine`, for tests that exercise
    acknowledge/resolve against a real record rather than tolerating 404.
    """
    db_alert = Alert(
        machine_id=machine.id,
        severity="HIGH",
        message="Test alert",
        probability=0.9,
        recommended_action="Inspect machine",
    )
    db_session.add(db_alert)
    db_session.commit()
    db_session.refresh(db_alert)
    return db_alert


@pytest.fixture()
def maintenance_task(db_session, machine):
    """A MaintenanceTask row tied to `machine`, for tests that exercise
    start/complete against a real record rather than tolerating 404.
    """
    db_task = MaintenanceTask(
        machine_id=machine.id,
        description="Test maintenance task",
        technician="Test Technician",
        status="OPEN",
    )
    db_session.add(db_task)
    db_session.commit()
    db_session.refresh(db_task)
    return db_task
