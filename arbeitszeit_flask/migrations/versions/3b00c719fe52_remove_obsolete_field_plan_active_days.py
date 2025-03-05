"""Remove obsolete field Plan.active_days

Revision ID: 3b00c719fe52
Revises: bdb92a1ce32c
Create Date: 2023-02-12 14:50:13.203584

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '3b00c719fe52'
down_revision = 'bdb92a1ce32c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('plan', schema=None) as batch_op:
        batch_op.drop_column('active_days')

    # ### end Alembic commands ###


def downgrade():
    Base = orm.declarative_base()
    class Plan(Base):
        __tablename__ = "plan"

        id = sa.Column(sa.String, primary_key=True)
        timeframe = sa.Column(sa.Numeric(), nullable=False)
        activation_date = sa.Column(sa.DateTime, nullable=True)

    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('plan', schema=None) as batch_op:
        batch_op.add_column(sa.Column('active_days', sa.INTEGER(), autoincrement=False, nullable=True))
    
    bind = op.get_bind()
    with orm.Session(bind=bind) as session:
        for plan in session.query(Plan):
            days_passed_since_activation = (datetime.now() - plan.activation_date).days
            plan.active_days = min(plan.timeframe, days_passed_since_activation)

    # ### end Alembic commands ###


