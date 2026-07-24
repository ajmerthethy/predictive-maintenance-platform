"""create maintenance tasks table

Revision ID: 7225f86f29e4
Revises: a67476165cae
Create Date: 2026-07-23 14:07:59.347187

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '7225f86f29e4'
down_revision: Union[str, Sequence[str], None] = 'a67476165cae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
