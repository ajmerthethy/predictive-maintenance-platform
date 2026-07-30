"""create alerts maintenance_tasks and predictions tables

Revision ID: 23d19eb73305
Revises: 527ce2bc57a1
Create Date: 2026-07-30 13:45:14.598939

These three tables have existed in every real deployment only as a side
effect of Base.metadata.create_all() at application startup. The migrations
that claimed to create alerts/maintenance_tasks (2db7ec19cd8e,
a67476165cae, 7225f86f29e4, f8a0fd660562) are empty no-op stubs, and no
migration for `predictions` ever existed — confirmed by running
`alembic upgrade head` against a fresh database and finding only
machines/sensor_readings/users present.

This migration creates the three tables for real. It imports the live ORM
models (rather than hand-writing sa.Column DDL, the usual convention for
this project's migrations) specifically to guarantee byte-for-byte parity
with whatever create_all already produced in production, and uses
checkfirst=True so it is a safe no-op there. This is a one-time
remediation for tables that were never properly under migration control —
new schema changes going forward should still use explicit op.* DDL like
the rest of this history.
"""
from typing import Sequence, Union

from alembic import op

from app.models.alert import Alert
from app.models.maintenance import MaintenanceTask
from app.models.prediction import Prediction

# revision identifiers, used by Alembic.
revision: str = '23d19eb73305'
down_revision: Union[str, Sequence[str], None] = '527ce2bc57a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    # Order respects foreign keys: maintenance_tasks references both
    # machines and alerts, so alerts must exist first.
    Alert.__table__.create(bind=bind, checkfirst=True)
    MaintenanceTask.__table__.create(bind=bind, checkfirst=True)
    Prediction.__table__.create(bind=bind, checkfirst=True)


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    # Reverse order: maintenance_tasks must drop before alerts.
    MaintenanceTask.__table__.drop(bind=bind, checkfirst=True)
    Prediction.__table__.drop(bind=bind, checkfirst=True)
    Alert.__table__.drop(bind=bind, checkfirst=True)
