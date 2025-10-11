"""Make user_id unique on company

Revision ID: e329522f1f5b
Revises: 52e3a1f4fc9a
Create Date: 2023-01-06 10:56:13.538362

"""
from alembic import op
import sqlalchemy as sa


revision = 'e329522f1f5b'
down_revision = '52e3a1f4fc9a'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('company') as batch_op:
        batch_op.create_unique_constraint('company_user_id_unique', ['user_id'])


def downgrade():
    with op.batch_alter_table('company') as batch_op:
        batch_op.drop_constraint('company_user_id_unique', type_='unique')
