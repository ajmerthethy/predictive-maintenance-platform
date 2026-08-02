"""add input_features and model_version to predictions

Revision ID: e7c3a5f19b02
Revises: d4b8f2a91c6e
Create Date: 2026-08-02 03:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'e7c3a5f19b02'
down_revision: Union[str, Sequence[str], None] = 'd4b8f2a91c6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    Makes every stored prediction independently reproducible/auditable:
    `input_features` snapshots the exact 5 sensor values fed to the model
    (POST /prediction/'s direct-input path has no backing SensorReading row
    to reconstruct them from later, and even where one exists it could
    since be edited or deleted), and `model_version` records which
    saved_models/vN/ produced it (see app/ml/model_loader.py). Both
    nullable - every prediction created before this migration has neither.

    Guarded with an existence check for the same reason as d4b8f2a91c6e:
    23d19eb73305 creates `predictions` by reflecting the live ORM model, so
    a fresh database already has these columns by the time this migration
    runs; an existing (already-deployed) database does not.
    """

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_columns = {
        column["name"] for column in inspector.get_columns("predictions")
    }

    if "input_features" not in existing_columns:
        op.add_column(
            'predictions',
            sa.Column('input_features', sa.JSON(), nullable=True),
        )

    if "model_version" not in existing_columns:
        op.add_column(
            'predictions',
            sa.Column('model_version', sa.String(), nullable=True),
        )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column('predictions', 'model_version')
    op.drop_column('predictions', 'input_features')
