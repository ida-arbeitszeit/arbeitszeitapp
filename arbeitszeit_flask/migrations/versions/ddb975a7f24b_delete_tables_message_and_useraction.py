"""delete tables message and useraction

Revision ID: ddb975a7f24b
Revises: c37965cc6adc
Create Date: 2022-06-19 19:21:27.512227

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "ddb975a7f24b"
down_revision = "c37965cc6adc"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("message")
    sa.Enum(name="useractiontype").drop(op.get_bind(), checkfirst=False)
    op.drop_table("user_action")


def downgrade():
    op.create_table(
        "user_action",
        sa.Column("id", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("reference", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column(
            "action_type",
            postgresql.ENUM(
                "answer_invite", "answer_cooperation_request", name="useractiontype"
            ),
            autoincrement=False,
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id", name="user_action_pkey"),
    )
    op.create_table(
        "message",
        sa.Column("id", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("sender", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("addressee", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("title", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("content", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("sender_remarks", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column("is_read", sa.BOOLEAN(), autoincrement=False, nullable=True),
        sa.Column("user_action", sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["user_action"], ["user_action.id"], name="message_user_action_fkey"
        ),
        sa.PrimaryKeyConstraint("id", name="message_pkey"),
    )
