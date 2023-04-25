"""Move confirmed_on from member/company to user table

Revision ID: fb341bf85b13
Revises: 35ec3b98a6cc
Create Date: 2023-04-20 17:02:15.682408

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'fb341bf85b13'
down_revision = '35ec3b98a6cc'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email_confirmed_on', sa.DateTime(), nullable=True))
    op.execute('''
UPDATE "user"
SET email_confirmed_on = member.confirmed_on
FROM member
WHERE "user".id = member.user_id AND
      member.confirmed_on IS NOT NULL;

UPDATE "user"
SET email_confirmed_on = company.confirmed_on
FROM company
WHERE
  "user".id = company.user_id AND
  company.confirmed_on IS NOT NULL;
UPDATE "user"
SET email_confirmed_on = NOW()
FROM accountant
WHERE
  "user".id = accountant.user_id;
    ''')
    with op.batch_alter_table('company', schema=None) as batch_op:
        batch_op.drop_column('confirmed_on')

    with op.batch_alter_table('member', schema=None) as batch_op:
        batch_op.drop_column('confirmed_on')


def downgrade():
    with op.batch_alter_table('member', schema=None) as batch_op:
        batch_op.add_column(sa.Column('confirmed_on', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))

    with op.batch_alter_table('company', schema=None) as batch_op:
        batch_op.add_column(sa.Column('confirmed_on', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.execute('''
UPDATE member
SET confirmed_on = "user".email_confirmed_on
FROM "user"
WHERE
    "user".id = member.user_id;
UPDATE company
SET confirmed_on = "user".email_confirmed_on
FROM "user"
WHERE
    "user".id = company.user_id;
    ''')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('email_confirmed_on')
