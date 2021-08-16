"""new column is_active for table plan

Revision ID: 3f66e07c61c0
Revises: 7b6cc29bf897
Create Date: 2021-08-15 14:39:58.654008

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3f66e07c61c0"
down_revision = "7b6cc29bf897"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("plan", sa.Column("is_active", sa.Boolean(), nullable=True))
    op.execute("UPDATE plan SET is_active = false")
    op.alter_column("plan", "is_active", nullable=False)


def downgrade():
    op.drop_column("plan", "is_active")
