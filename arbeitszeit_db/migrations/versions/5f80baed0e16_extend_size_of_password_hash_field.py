"""Extend size of password hash field

Revision ID: 5f80baed0e16
Revises: c389d9c0145e
Create Date: 2024-01-10 16:44:07.597883
"""
import sqlalchemy as sa
from alembic import op

revision = "5f80baed0e16"
down_revision = "c389d9c0145e"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.alter_column(
            "password",
            existing_type=sa.VARCHAR(length=100),
            type_=sa.String(length=300),
            existing_nullable=False,
        )


def downgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.alter_column(
            "password",
            existing_type=sa.String(length=300),
            type_=sa.VARCHAR(length=100),
            existing_nullable=False,
        )
