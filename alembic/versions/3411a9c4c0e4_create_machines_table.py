"""create machines table

Revision ID: 3411a9c4c0e4
Revises:
Create Date: 2026-07-22 13:03:43.828865
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '3411a9c4c0e4'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None





def upgrade() -> None:
    op.create_table(
        'machines',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('name', sa.VARCHAR(), nullable=False),
        sa.Column('location', sa.VARCHAR(), nullable=False),
        sa.Column('manufacturer', sa.VARCHAR(), nullable=True),
        sa.Column('install_date', sa.DATE(), nullable=True),
        sa.Column('status', sa.VARCHAR(), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('machines_pkey'))
    )


def downgrade() -> None:
    op.drop_table('machines')
