"""add accounts table and account_id to users and machines

Revision ID: cc1cc65dad25
Revises: 23d19eb73305
Create Date: 2026-07-31 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'cc1cc65dad25'
down_revision: Union[str, Sequence[str], None] = '23d19eb73305'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DEFAULT_ACCOUNT_NAME = "Default Account"


def upgrade() -> None:
    """Upgrade schema.

    Introduces the tenant/account boundary that was previously missing
    entirely - every Machine (and everything hanging off it) and every
    User now belongs to exactly one Account.

    Backfills a single "Default Account" and assigns every existing user
    and machine to it, so this is a no-op from the current single-customer
    deployment's point of view: nothing that already works stops working,
    and nothing existing loses access to anything it could already see.
    A genuinely second account only comes into existence when someone
    explicitly provisions one (see scripts/create_user.py).
    """

    op.create_table(
        'accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_accounts_id'), 'accounts', ['id'], unique=False)
    op.create_index(op.f('ix_accounts_name'), 'accounts', ['name'], unique=True)

    default_account = sa.table(
        'accounts',
        sa.column('id', sa.Integer),
        sa.column('name', sa.String),
    )
    op.bulk_insert(default_account, [{'name': DEFAULT_ACCOUNT_NAME}])

    # --- users.account_id ---
    op.add_column('users', sa.Column('account_id', sa.Integer(), nullable=True))
    op.execute(
        f"UPDATE users SET account_id = "
        f"(SELECT id FROM accounts WHERE name = '{DEFAULT_ACCOUNT_NAME}')"
    )
    op.alter_column('users', 'account_id', nullable=False)
    op.create_foreign_key(
        'fk_users_account_id_accounts', 'users', 'accounts', ['account_id'], ['id']
    )

    # --- machines.account_id ---
    op.add_column('machines', sa.Column('account_id', sa.Integer(), nullable=True))
    op.execute(
        f"UPDATE machines SET account_id = "
        f"(SELECT id FROM accounts WHERE name = '{DEFAULT_ACCOUNT_NAME}')"
    )
    op.alter_column('machines', 'account_id', nullable=False)
    op.create_foreign_key(
        'fk_machines_account_id_accounts', 'machines', 'accounts', ['account_id'], ['id']
    )
    op.create_index(op.f('ix_machines_account_id'), 'machines', ['account_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(op.f('ix_machines_account_id'), table_name='machines')
    op.drop_constraint('fk_machines_account_id_accounts', 'machines', type_='foreignkey')
    op.drop_column('machines', 'account_id')

    op.drop_constraint('fk_users_account_id_accounts', 'users', type_='foreignkey')
    op.drop_column('users', 'account_id')

    op.drop_index(op.f('ix_accounts_name'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_id'), table_name='accounts')
    op.drop_table('accounts')
