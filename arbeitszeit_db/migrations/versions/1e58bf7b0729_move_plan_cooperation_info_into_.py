"""Move plan cooperation info into association plan_cooperation table

Revision ID: 1e58bf7b0729
Revises: 809a9eb543c1
Create Date: 2024-02-20 17:59:17.877444

"""
from alembic import op
import sqlalchemy as sa


revision = "1e58bf7b0729"
down_revision = "809a9eb543c1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "plan_cooperation",
        sa.Column("plan", sa.String(), nullable=False),
        sa.Column("cooperation", sa.String(), nullable=False),
        sa.ForeignKeyConstraint(
            ["cooperation"],
            ["cooperation.id"],
        ),
        sa.ForeignKeyConstraint(
            ["plan"],
            ["plan.id"],
        ),
        sa.PrimaryKeyConstraint("plan"),
    )
    op.execute(
        """
        INSERT INTO "plan_cooperation" ("plan", "cooperation")
        SELECT "plan"."id" AS "plan", "plan"."cooperation" AS cooperation
        FROM "plan"
        WHERE cooperation IS NOT NULL
        """
    )
    with op.batch_alter_table("plan", schema=None) as batch_op:
        batch_op.drop_column("cooperation")


def downgrade():
    with op.batch_alter_table("plan", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "cooperation",
                sa.String(),
                nullable=True,
            )
        )
        batch_op.create_foreign_key(
            constraint_name="plan_cooperation_fkey",
            referent_table="cooperation",
            local_cols=["cooperation"],
            remote_cols=["id"],
        )
    op.execute("""
        UPDATE "plan"
        SET cooperation = "plan_cooperation".cooperation
        FROM "plan_cooperation"
        WHERE "plan_cooperation"."plan" = "plan"."id"
    """)
    op.drop_table("plan_cooperation")
