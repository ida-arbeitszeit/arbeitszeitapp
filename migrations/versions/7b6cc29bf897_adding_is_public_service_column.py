"""adding is_public_service column

Revision ID: 7b6cc29bf897
Revises: a9cedb1aedfa
Create Date: 2021-08-11 23:06:41.879745

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7b6cc29bf897"
down_revision = "a8906c6f44bc"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("plan", sa.Column("is_public_service", sa.Boolean(), nullable=True))
    op.execute("UPDATE plan SET is_public_service = false")
    op.alter_column("plan", "is_public_service", nullable=False)


def downgrade():
    op.drop_column("plan", "is_public_service")
