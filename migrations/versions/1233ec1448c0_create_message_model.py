"""Create Message model

Revision ID: 1233ec1448c0
Revises: 7198e8c48018
Create Date: 2021-10-24 12:38:49.649089

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1233ec1448c0"
down_revision = "6cc564ebe386"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "message",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("sender", sa.String(), nullable=True),
        sa.Column("addressee", sa.String(), nullable=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("content", sa.String(), nullable=True),
        sa.Column(
            "user_action", sa.Enum("answer_invite", name="useraction"), nullable=True
        ),
        sa.Column("sender_remarks", sa.String(), nullable=True),
        sa.Column("is_read", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("message")
    sa.Enum(name="useraction").drop(op.get_bind(), checkfirst=False)

    # ### end Alembic commands ###
