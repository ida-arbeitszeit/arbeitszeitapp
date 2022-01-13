"""add registered_on and confirmed_on to comp

Revision ID: fb89625b2d12
Revises: c0dbe17daefe
Create Date: 2022-01-11 17:15:57.832987

"""
from alembic import op
import sqlalchemy as sa

## UNCOMMENT THIS AND ADAPT DOWN_REVISION
## (HERE AND ON TOP OF FILE)
## WHEN PR IS READY FOR MIGRATION

## revision identifiers, used by Alembic.
# revision = "fb89625b2d12"
# down_revision = "c0dbe17daefe"
# branch_labels = None
# depends_on = None


def upgrade():
    # set default values for registered_on and confirmed_on
    op.add_column("company", sa.Column("registered_on", sa.DateTime(), nullable=True))
    op.execute("UPDATE company SET registered_on = '2021-12-21 00:00:00.000'")
    op.alter_column("company", "registered_on", nullable=False)

    op.add_column("company", sa.Column("confirmed_on", sa.DateTime(), nullable=True))
    op.execute("UPDATE company SET confirmed_on = '2021-12-21 01:00:00.000'")


def downgrade():
    op.drop_column("company", "confirmed_on")
    op.drop_column("company", "registered_on")
