"""changining column timeframe to timeframe_in_days

Revision ID: dd6b86594f2d
Revises: 
Create Date: 2021-07-20 17:36:35.865796

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "dd6b86594f2d"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "plan", "timeframe", new_column_name="timeframe_in_days", type_=sa.Integer
    )


def downgrade():
    op.alter_column(
        "plan", "timeframe_in_days", new_column_name="timeframe", type_=sa.Numeric
    )
