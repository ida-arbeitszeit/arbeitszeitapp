"""Non-nullable transactions in consumption tables

Revision ID: 9ab8e18b4d0e
Revises: 8a3b2c1d0e9f
Create Date: 2025-05-18 02:07:45.768231

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9ab8e18b4d0e'
down_revision: Union[str, None] = '8a3b2c1d0e9f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('private_consumption', 'transaction_id',
               nullable=False)
    op.alter_column('productive_consumption', 'transaction_id',
               nullable=False)


def downgrade() -> None:
    pass
