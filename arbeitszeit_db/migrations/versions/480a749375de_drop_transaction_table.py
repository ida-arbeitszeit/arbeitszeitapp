"""drop transaction table

Revision ID: 480a749375de
Revises: 8b51e4ca0073
Create Date: 2025-07-01 23:16:25.312012

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '480a749375de'
down_revision: Union[str, None] = '8b51e4ca0073'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table('transaction')


def downgrade() -> None:
    op.create_table('transaction',
    sa.Column('id', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('date', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('sending_account', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('receiving_account', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('purpose', sa.VARCHAR(length=1000), autoincrement=False, nullable=False),
    sa.Column('amount_sent', sa.NUMERIC(), autoincrement=False, nullable=False),
    sa.Column('amount_received', sa.NUMERIC(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['receiving_account'], ['account.id'], name='transaction_receiving_account_fkey'),
    sa.ForeignKeyConstraint(['sending_account'], ['account.id'], name='transaction_sending_account_fkey'),
    sa.PrimaryKeyConstraint('id', name='transaction_pkey')
    )
