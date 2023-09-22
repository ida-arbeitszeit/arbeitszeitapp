"""add on delete cascade on plan_review fkey

Revision ID: e25cf496eef3
Revises: c56e8291e74d
Create Date: 2023-09-21 19:18:00.762149

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e25cf496eef3'
down_revision = 'c56e8291e74d'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('plan_review', schema=None) as batch_op:
        batch_op.drop_constraint('plan_review_plan_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key('plan_review_plan_id_fkey', 'plan', ['plan_id'], ['id'], ondelete='CASCADE')

def downgrade():
    with op.batch_alter_table('plan_review', schema=None) as batch_op:
        batch_op.drop_constraint('plan_review_plan_id_fkey', type_='foreignkey')
        batch_op.create_foreign_key('plan_review_plan_id_fkey', 'plan', ['plan_id'], ['id'])
