"""Remove is_available on plan table

Revision ID: 809a9eb543c1
Revises: 5f80baed0e16
Create Date: 2024-02-03 12:00:41.412156
"""
from alembic import op
import sqlalchemy as sa


revision = "809a9eb543c1"
down_revision = "5f80baed0e16"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("plan", schema=None) as batch_op:
        batch_op.drop_column("is_available")


def downgrade():
    with op.batch_alter_table("plan", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("is_available", sa.BOOLEAN(), autoincrement=False, nullable=True)
        )
    op.execute("UPDATE plan SET is_available = true")
    op.alter_column('plan', 'is_available', nullable=False)
