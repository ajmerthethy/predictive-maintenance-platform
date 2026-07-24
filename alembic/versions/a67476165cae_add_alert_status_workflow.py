"""add alert status workflow

Revision ID: a67476165cae
Revises: 2db7ec19cd8e
Create Date: 2026-07-23 13:36:25.225094

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a67476165cae'
down_revision: Union[str, Sequence[str], None] = '2db7ec19cd8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
