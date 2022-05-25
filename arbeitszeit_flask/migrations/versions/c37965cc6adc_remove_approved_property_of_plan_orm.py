"""Remove .approved property of Plan ORM

Revision ID: c37965cc6adc
Revises: f5987219755a
Create Date: 2022-05-23 21:38:27.395938

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c37965cc6adc'
down_revision = 'f5987219755a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('plan', 'approved')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('plan', sa.Column('approved', sa.BOOLEAN(), autoincrement=False, nullable=True))
    with op.batch_alter_table('plan') as batch_op:
        batch_op.execute("""
            UPDATE plan
            SET approved = (
                SELECT CASE
                    WHEN plan_old.approval_date IS NULL THEN false
                    ELSE true
                END
                FROM plan as plan_old
                WHERE plan_old.id = plan.id
            )
        """)
    op.alter_column('plan', 'approved', nullable=False)
    # ### end Alembic commands ###