"""Delete old database types

Revision ID: 0f1f3b156d62
Revises: d6f685a49a41
Create Date: 2025-04-21 21:36:08.624847

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f1f3b156d62'
down_revision: Union[str, None] = 'd6f685a49a41'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
