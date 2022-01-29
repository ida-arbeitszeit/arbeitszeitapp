"""add is_available to plan table

Revision ID: 87a9fb39c257
Revises: 803d7861bcbc
Create Date: 2021-11-02 16:09:50.065710

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "87a9fb39c257"
down_revision = "803d7861bcbc"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("plan") as batch_op:
        batch_op.add_column(sa.Column("is_available", sa.Boolean(), nullable=True))
    with op.batch_alter_table("plan") as batch_op:
        batch_op.execute("UPDATE plan SET is_available = False")
        batch_op.execute("UPDATE plan SET is_available = True WHERE plan.is_active")
        batch_op.alter_column("is_available", nullable=False)


def downgrade():
    with op.batch_alter_table("plan") as batch_op:
        batch_op.drop_column("is_available")
