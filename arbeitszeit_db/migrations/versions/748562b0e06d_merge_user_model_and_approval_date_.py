"""merge user model and approval date changes

Revision ID: 748562b0e06d
Revises: 51153c9ba707, bc1b2a684dfb
Create Date: 2022-06-30 19:28:49.110667

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '748562b0e06d'
down_revision = ('51153c9ba707', 'bc1b2a684dfb')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
