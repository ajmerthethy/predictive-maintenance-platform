"""add failure label to sensor readings

Revision ID: fa2eddedf534
Revises: 7f91dcb2c58c
Create Date: 2026-07-22 16:15:10.808422

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fa2eddedf534'
down_revision: Union[str, Sequence[str], None] = '7f91dcb2c58c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'sensor_readings',
        sa.Column('failure_label', sa.Boolean(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column(
        'sensor_readings',
        'failure_label'
    )
