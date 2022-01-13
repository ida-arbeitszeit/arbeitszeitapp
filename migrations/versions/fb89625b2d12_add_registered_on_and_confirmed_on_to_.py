"""add registered_on and confirmed_on to comp

Revision ID: fb89625b2d12
Revises: 6ad4ca971b73
Create Date: 2022-01-11 17:15:57.832987

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "fb89625b2d12"
down_revision = "6ad4ca971b73"
branch_labels = None
depends_on = None


def upgrade():
    # set default values for registered_on and confirmed_on
    op.add_column("company", sa.Column("registered_on", sa.DateTime(), nullable=True))
    op.execute("UPDATE company SET registered_on = '2021-12-21 00:00:00.000'")
    with op.batch_alter_table("company") as batch_op:
        batch_op.alter_column("registered_on", nullable=False)

    op.add_column("company", sa.Column("confirmed_on", sa.DateTime(), nullable=True))
    op.execute("UPDATE company SET confirmed_on = '2021-12-21 01:00:00.000'")


def downgrade():
    with op.batch_alter_table("company") as batch_op:
        batch_op.drop_column("confirmed_on")
        batch_op.drop_column("registered_on")
