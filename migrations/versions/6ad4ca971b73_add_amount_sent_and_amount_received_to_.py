"""add amount_sent and amount_received to Transaction

Revision ID: 6ad4ca971b73
Revises: c0dbe17daefe
Create Date: 2022-01-10 20:33:27.135770

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6ad4ca971b73"
down_revision = "c0dbe17daefe"
branch_labels = None
depends_on = None


def upgrade():
    # This code copies the rows of column 'amount' and pastes them *both* into amount_sent and amount_received.
    # Afterwards column 'amount' gets deleted

    op.add_column("transaction", sa.Column("amount_sent", sa.Numeric(), nullable=True))
    with op.batch_alter_table("transaction") as batch_op:
        batch_op.execute(
            """UPDATE "transaction" SET amount_sent = amount"""
        )  # "transaction" is a keyword in sqlite
        batch_op.alter_column("amount_sent", nullable=False)

    op.add_column(
        "transaction", sa.Column("amount_received", sa.Numeric(), nullable=True)
    )
    with op.batch_alter_table("transaction") as batch_op:
        batch_op.execute("""UPDATE "transaction" SET amount_received = amount""")
        batch_op.alter_column("amount_received", nullable=False)

    with op.batch_alter_table("transaction") as batch_op:
        batch_op.drop_column("amount")


def downgrade():
    # Before amount_received and amount_sent gets deleted, the old column 'amount'
    # gets created and receives the content of amount_sent
    op.add_column(
        "transaction",
        sa.Column("amount", sa.NUMERIC(), autoincrement=False, nullable=True),
    )
    op.execute("""UPDATE "transaction" SET amount = amount_sent""")

    with op.batch_alter_table("transaction") as batch_op:
        batch_op.alter_column("amount", nullable=False)
        batch_op.drop_column("amount_received")
        batch_op.drop_column("amount_sent")
