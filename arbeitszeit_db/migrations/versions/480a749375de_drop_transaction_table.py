"""drop transaction table

Revision ID: 480a749375de
Revises:
Create Date: 2025-07-01 23:16:25.312012

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '480a749375de'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('transaction_receiving_account_fkey', 'transaction', type_='foreignkey', if_exists=True)
    op.drop_constraint('transaction_sending_account_fkey', 'transaction', type_='foreignkey', if_exists=True)
    op.drop_constraint('transaction_pkey', 'transaction', type_='primary', if_exists=True)
    op.drop_table('transaction', if_exists=True)


def downgrade() -> None:
    pass
