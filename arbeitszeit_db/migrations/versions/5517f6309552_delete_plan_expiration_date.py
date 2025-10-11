"""delete Plan.expiration_date

Revision ID: 5517f6309552
Revises: f8d8f7d8904e
Create Date: 2022-11-13 16:04:16.564694

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '5517f6309552'
down_revision = 'f8d8f7d8904e'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('plan') as batch_op:
        batch_op.drop_column('expiration_date')


def downgrade():
    with op.batch_alter_table('plan') as batch_op:
        batch_op.add_column(sa.Column('expiration_date', sa.DateTime(), autoincrement=False, nullable=True))
