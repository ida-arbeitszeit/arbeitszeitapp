"""Create email table

Revision ID: 7a550048df32
Revises: 8cdaf3b82da6
Create Date: 2023-06-21 05:44:25.570799

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "7a550048df32"
down_revision = "8cdaf3b82da6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "email",
        sa.Column("address", sa.String(), nullable=False),
        sa.Column("confirmed_on", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("address"),
    )
    op.execute(
        """
        INSERT INTO email (address, confirmed_on)
        SELECT "user".email AS address, "user".email_confirmed_on AS confirmed_on
        FROM "user"
    """
    )
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(sa.Column("email_address", sa.String(), nullable=True))
        batch_op.create_unique_constraint(
            "user_email_address_unique", ["email_address"]
        )
        batch_op.create_foreign_key(
            "user_email_address_fkey", "email", ["email_address"], ["address"]
        )
    op.execute(
        """
        UPDATE "user"
        SET email_address = "user".email
    """
    )
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.alter_column(
            "email_address", existing_type=sa.VARCHAR(), nullable=False
        )
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_constraint("user_email_key", type_="unique")
        batch_op.drop_column("email_confirmed_on")
        batch_op.drop_column("email")


def downgrade():
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "email", sa.VARCHAR(length=100), autoincrement=False, nullable=True
            )
        )
        batch_op.add_column(
            sa.Column(
                "email_confirmed_on",
                postgresql.TIMESTAMP(),
                autoincrement=False,
                nullable=True,
            )
        )
        batch_op.create_unique_constraint("user_email_key", ["email"])
    op.execute(
        """
        UPDATE "user"
        SET email = e.address, email_confirmed_on = e.confirmed_on
        FROM email e
        WHERE e.address = "user".email_address
    """
    )
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.alter_column("email", existing_type=sa.VARCHAR(), nullable=False)
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.alter_column(
            "email_address", existing_type=sa.VARCHAR(), nullable=True
        )
    with op.batch_alter_table("user", schema=None) as batch_op:
        batch_op.drop_constraint("user_email_address_fkey", type_="foreignkey")
        batch_op.drop_constraint("user_email_address_unique", type_="unique")
        batch_op.drop_column("email_address")
    op.drop_table("email")
