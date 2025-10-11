"""Remove plan.activation_date column

Revision ID: 93342c4aa821
Revises: 19595c8bb59b
Create Date: 2025-04-19 22:59:52.410706

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '93342c4aa821'
down_revision: Union[str, None] = '19595c8bb59b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('plan', 'activation_date')


def downgrade() -> None:
    op.add_column('plan', sa.Column('activation_date', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.execute("""
        UPDATE plan
        SET activation_date = pr.approval_date
        FROM plan_review pr
        WHERE plan.id = pr.plan_id
    """)
