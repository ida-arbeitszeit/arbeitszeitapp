"""delete column active from Offer

Revision ID: d5f7df16a723
Revises: 5ccb2cf7d04c
Create Date: 2021-09-26 22:06:39.515537

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d5f7df16a723"
down_revision = "5ccb2cf7d04c"
branch_labels = None
depends_on = None


def upgrade():
    # batch mode required by sqlite
    with op.batch_alter_table("offer") as batch_op:
        batch_op.drop_column("active")


def downgrade():
    # batch mode required by sqlite
    with op.batch_alter_table("offer") as batch_op:
        batch_op.add_column(
            sa.Column("active", sa.BOOLEAN(), autoincrement=False, nullable=True)
        )
    with op.batch_alter_table("offer") as batch_op:
        batch_op.execute("UPDATE offer SET active = true")
        batch_op.alter_column("active", nullable=False)
