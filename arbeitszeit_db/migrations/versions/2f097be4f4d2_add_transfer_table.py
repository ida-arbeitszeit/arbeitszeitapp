"""Add transfer table

Revision ID: 2f097be4f4d2
Revises: eb928efc4311
Create Date: 2025-03-15 16:45:46.179907

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f097be4f4d2'
down_revision: Union[str, None] = 'eb928efc4311'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the new Transfer table
    op.create_table(
        'transfer',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('debit_account', sa.String(), nullable=False),
        sa.Column('credit_account', sa.String(), nullable=False),
        sa.Column('value', sa.Numeric(), nullable=False),
        sa.ForeignKeyConstraint(['debit_account'], ['account.id'], ),
        sa.ForeignKeyConstraint(['credit_account'], ['account.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add indexes to improve query performance
    op.create_index(op.f('ix_transfer_debit_account'), 'transfer', ['debit_account'], unique=False)
    op.create_index(op.f('ix_transfer_credit_account'), 'transfer', ['credit_account'], unique=False)
    op.create_index(op.f('ix_transfer_date'), 'transfer', ['date'], unique=False)


def downgrade() -> None:
    # Drop the indexes first
    op.drop_index(op.f('ix_transfer_date'), table_name='transfer')
    op.drop_index(op.f('ix_transfer_credit_account'), table_name='transfer')
    op.drop_index(op.f('ix_transfer_debit_account'), table_name='transfer')
    
    # Then drop the table
    op.drop_table('transfer')