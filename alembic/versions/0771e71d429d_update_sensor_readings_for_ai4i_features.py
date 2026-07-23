"""update sensor readings for ai4i features

Revision ID: 0771e71d429d
Revises: f8a0fd660562
Create Date: 2026-07-23 18:57:17.644312

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0771e71d429d'
down_revision: Union[str, Sequence[str], None] = 'f8a0fd660562'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        'sensor_readings',
        sa.Column(
            'air_temperature',
            sa.Float(),
            nullable=True
        )
    )

    op.add_column(
        'sensor_readings',
        sa.Column(
            'process_temperature',
            sa.Float(),
            nullable=True
        )
    )

    op.add_column(
        'sensor_readings',
        sa.Column(
            'rotational_speed',
            sa.Float(),
            nullable=True
        )
    )

    op.add_column(
        'sensor_readings',
        sa.Column(
            'torque',
            sa.Float(),
            nullable=True
        )
    )

    op.add_column(
        'sensor_readings',
        sa.Column(
            'tool_wear',
            sa.Float(),
            nullable=True
        )
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        'sensor_readings',
        'tool_wear'
    )

    op.drop_column(
        'sensor_readings',
        'torque'
    )

    op.drop_column(
        'sensor_readings',
        'rotational_speed'
    )

    op.drop_column(
        'sensor_readings',
        'process_temperature'
    )

    op.drop_column(
        'sensor_readings',
        'air_temperature'
    )