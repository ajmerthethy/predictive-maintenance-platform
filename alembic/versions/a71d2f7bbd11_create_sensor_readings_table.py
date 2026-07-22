"""create sensor readings table

Revision ID: a71d2f7bbd11
Revises: feedde6557a5
Create Date: 2026-07-22 14:26:16.216234

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a71d2f7bbd11'
down_revision: Union[str, Sequence[str], None] = '3411a9c4c0e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'sensor_readings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('machine_id', sa.Integer(), nullable=False),
        sa.Column('temperature', sa.Float(), nullable=False),
        sa.Column('vibration', sa.Float(), nullable=False),
        sa.Column('pressure', sa.Float(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ['machine_id'],
            ['machines.id'],
        ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_index(
        op.f('ix_sensor_readings_id'),
        'sensor_readings',
        ['id'],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f('ix_sensor_readings_id'),
        table_name='sensor_readings'
    )

    op.drop_table('sensor_readings')
