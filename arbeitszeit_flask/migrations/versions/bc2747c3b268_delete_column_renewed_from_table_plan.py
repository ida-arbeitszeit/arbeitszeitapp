"""delete column renewed from table Plan

Revision ID: bc2747c3b268
Revises: 5e541f042231
Create Date: 2022-03-17 23:35:38.116844

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "bc2747c3b268"
down_revision = "5e541f042231"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("plan") as batch_op:
        batch_op.drop_column("renewed")


def downgrade():
    with op.batch_alter_table("plan") as batch_op:
        batch_op.add_column(sa.Column("renewed", sa.Boolean(), nullable=True))
    with op.batch_alter_table("plan") as batch_op:
        batch_op.execute("UPDATE plan SET renewed = False")
        batch_op.alter_column("renewed", nullable=False)
