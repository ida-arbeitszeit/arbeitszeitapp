"""Remove account_type field from Account table

Revision ID: 35ec3b98a6cc
Revises: 925b1eb7c332
Create Date: 2023-03-28 09:45:31.433012

"""
from uuid import uuid4
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = '35ec3b98a6cc'
down_revision = '925b1eb7c332'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.drop_column('account_type')


def downgrade():
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.add_column(sa.Column('account_type', postgresql.ENUM('p', 'r', 'a', 'prd', 'member', 'accounting', name='accounttypes'), autoincrement=False, nullable=True))
    op.execute('''
UPDATE account
SET account_type = 'p'
FROM company
WHERE company.p_account = account.id;

UPDATE account
SET account_type = 'r'
FROM company
WHERE company.r_account = account.id;

UPDATE account
SET account_type = 'a'
FROM company
WHERE company.a_account = account.id;

UPDATE account
SET account_type = 'prd'
FROM company
WHERE company.prd_account = account.id;

UPDATE account
SET account_type = 'member'
FROM member
WHERE member.account = account.id;

UPDATE account
SET account_type = 'accounting'
FROM social_accounting
WHERE social_accounting.account = account.id;
    ''')
    with op.batch_alter_table('account', schema=None) as batch_op:
        batch_op.alter_column('account_type', nullable=False)
