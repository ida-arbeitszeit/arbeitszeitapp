"""Create PlanReview model and delete obsolete attributes from Plan

Revision ID: f8d8f7d8904e
Revises: 4444372436e2
Create Date: 2022-10-03 13:40:03.374890

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from uuid import uuid4


# revision identifiers, used by Alembic.
revision = "f8d8f7d8904e"
down_revision = "4444372436e2"
branch_labels = None
depends_on = None


def upgrade():
    plan_review_table = op.create_table(
        "plan_review",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("approval_date", sa.DateTime(), nullable=True),
        sa.Column("approval_reason", sa.String(length=1000), nullable=True),
        sa.Column("plan_id", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["plan_id"],
            ["plan.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    plan_table = sa.Table(
        "plan",
        sa.MetaData(),
        sa.Column("id", sa.String()),
        sa.Column("approval_date", sa.DateTime(), nullable=True),
        sa.Column("approval_reason", sa.String(length=1000), nullable=True),
    )
    connection = op.get_bind()
    for plan in connection.execute(plan_table.select()):
        values = dict(
            id=str(uuid4()),
            approval_date=plan.approval_date,
            approval_reason=plan.approval_reason,
            plan_id=plan.id,
        )
        connection.execute(plan_review_table.insert().values(values))
    op.drop_column("plan", "approval_date")
    op.drop_column("plan", "approval_reason")


def downgrade():
    op.add_column(
        "plan",
        sa.Column(
            "approval_reason",
            sa.VARCHAR(length=1000),
            autoincrement=False,
            nullable=True,
        ),
    )
    op.add_column(
        "plan",
        sa.Column(
            "approval_date", postgresql.TIMESTAMP(), autoincrement=False, nullable=True
        ),
    )
    plan_review_table = sa.Table(
        "plan_review",
        sa.MetaData(),
        sa.Column("approval_date", sa.DateTime(), nullable=True),
        sa.Column("approval_reason", sa.String(length=1000), nullable=True),
        sa.Column("plan_id", sa.String()),
    )
    plan_table = sa.Table(
        "plan",
        sa.MetaData(),
        sa.Column("id", sa.String()),
        sa.Column("approval_date", sa.DateTime(), nullable=True),
        sa.Column("approval_reason", sa.String(length=1000), nullable=True),
    )
    connection = op.get_bind()
    for review in connection.execute(plan_review_table.select()):
        values = dict(
            approval_date=review.approval_date,
            approval_reason=review.approval_reason,
        )
        connection.execute(
            plan_table.update()
            .where(plan_review_table.c.plan_id == plan_table.c.id)
            .values(values)
        )
    op.drop_constraint("plan_review_plan_id_fkey", "plan_review", type_="foreignkey")
    op.drop_table("plan_review")
