"""Remove social accounting account

Revision ID: 4fd90069eb82
Revises: 480a749375de
Create Date: 2025-08-02 07:20:54.450970

"""
from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers, used by Alembic.
revision: str = '4fd90069eb82'
down_revision: Union[str, None] = '480a749375de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('social_accounting_account_fkey', 'social_accounting', type_='foreignkey')
    op.drop_column('social_accounting', 'account')


def downgrade() -> None:
    op.add_column('social_accounting', sa.Column('account', sa.VARCHAR(), autoincrement=False, nullable=True))
    
    # Generate a valid account ID and add it to the social_accounting table.
    social_accounting = table('social_accounting', column('account', sa.VARCHAR()))
    op.execute(social_accounting.update().values(account=generate_valid_account_id()))
    
    op.alter_column('social_accounting', 'account', nullable=False)
    op.create_foreign_key('social_accounting_account_fkey', 'social_accounting', 'account', ['account'], ['id'])


def generate_valid_account_id() -> str:
    conn = op.get_bind()
    new_id = generate_uuid()
    conn.execute(
        sa.text("INSERT INTO account (id) VALUES (:id)"),
        {"id": new_id}
    )
    return new_id


def generate_uuid() -> str:
    return str(uuid4())
