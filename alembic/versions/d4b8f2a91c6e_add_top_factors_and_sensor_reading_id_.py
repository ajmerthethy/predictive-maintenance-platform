"""add top_factors and sensor_reading_id to predictions

Revision ID: d4b8f2a91c6e
Revises: cc1cc65dad25
Create Date: 2026-08-02 02:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'd4b8f2a91c6e'
down_revision: Union[str, Sequence[str], None] = 'cc1cc65dad25'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    Lets a stored Prediction row be read back later without re-running
    inference: `top_factors` persists the SHAP explanation computed at
    prediction time, and `sensor_reading_id` links back to the reading (if
    any) that produced it. Both nullable - POST /prediction/'s direct-input
    path has no backing SensorReading row, and every prediction created
    before this migration has neither. Required for GET /prediction/... and
    GET /recommendations/... to stop performing inference as a side effect
    of a read (see ML/MLOps audit, Immediate recommendation #2).

    Guarded with an existence check (mirroring 23d19eb73305's checkfirst=True
    precedent) rather than a plain op.add_column: 23d19eb73305 creates this
    table via Prediction.__table__.create(..., checkfirst=True), i.e. from
    whatever the live ORM model looks like at migration-run time - so on any
    database built from scratch after this column was added to the model,
    `predictions` already has both columns by the time this migration runs.
    On an existing database that already had `predictions` before this
    change (e.g. today's production data), these columns are genuinely
    still missing and this migration adds them for real.
    """

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {
        column["name"] for column in inspector.get_columns("predictions")
    }

    if "sensor_reading_id" not in existing_columns:
        op.add_column(
            'predictions',
            sa.Column('sensor_reading_id', sa.Integer(), nullable=True),
        )

    existing_fks = {
        fk["name"] for fk in inspector.get_foreign_keys("predictions")
    }

    if "fk_predictions_sensor_reading_id_sensor_readings" not in existing_fks:
        op.create_foreign_key(
            'fk_predictions_sensor_reading_id_sensor_readings',
            'predictions',
            'sensor_readings',
            ['sensor_reading_id'],
            ['id'],
        )

    if "top_factors" not in existing_columns:
        op.add_column(
            'predictions',
            sa.Column('top_factors', sa.JSON(), nullable=True),
        )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column('predictions', 'top_factors')

    op.drop_constraint(
        'fk_predictions_sensor_reading_id_sensor_readings',
        'predictions',
        type_='foreignkey',
    )
    op.drop_column('predictions', 'sensor_reading_id')
