"""create alerts table

Revision ID: 2db7ec19cd8e
Revises: a7e51dff993f
Create Date: 2026-07-23 13:22:44.840801

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '2db7ec19cd8e'
down_revision: Union[str, Sequence[str], None] = 'a7e51dff993f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass



def downgrade() -> None:
    """Downgrade schema."""
    pass
