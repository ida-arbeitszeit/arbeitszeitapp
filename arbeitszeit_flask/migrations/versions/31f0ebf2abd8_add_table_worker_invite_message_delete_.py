"""add table worker invite message, delete table message

Revision ID: 31f0ebf2abd8
Revises: c37965cc6adc
Create Date: 2022-05-29 12:18:49.255463

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "31f0ebf2abd8"
down_revision = "c37965cc6adc"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "worker_invite_message",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("invite_id", sa.String(), nullable=False),
        sa.Column("company", sa.String(), nullable=False),
        sa.Column("worker", sa.String(), nullable=False),
        sa.Column("is_read", sa.Boolean(), nullable=True),
        sa.Column("creation_date", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["company"],
            ["company.id"],
        ),
        sa.ForeignKeyConstraint(
            ["invite_id"],
            ["company_work_invite.id"],
        ),
        sa.ForeignKeyConstraint(
            ["worker"],
            ["member.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.drop_table("message")
    op.drop_table("user_action")
    op.execute("DROP TYPE IF EXISTS useractiontype CASCADE")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
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
    op.drop_table("worker_invite_message")
    # ### end Alembic commands ###
