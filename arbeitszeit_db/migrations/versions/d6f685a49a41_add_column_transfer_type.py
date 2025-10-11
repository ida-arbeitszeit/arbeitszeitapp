"""Add column transfer.type

Revision ID: d6f685a49a41
Revises: 93342c4aa821
Create Date: 2025-04-21 13:18:41.083474

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'd6f685a49a41'
down_revision: Union[str, None] = '93342c4aa821'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the enum type first
    transfertype = postgresql.ENUM('credit_p', 'credit_r', 'credit_a', 'credit_public_p', 'credit_public_r', 'credit_public_a', 'private_consumption', 'productive_consumption_p', 'productive_consumption_r', 'compensation_for_coop', 'compensation_for_company', 'work_certificates', 'taxes', name='transfertype')
    transfertype.create(op.get_bind())
    
    # Then add the column using the created enum type
    op.add_column('transfer', sa.Column('type', sa.Enum('credit_p', 'credit_r', 'credit_a', 'credit_public_p', 'credit_public_r', 'credit_public_a', 'private_consumption', 'productive_consumption_p', 'productive_consumption_r', 'compensation_for_coop', 'compensation_for_company', 'work_certificates', 'taxes', name='transfertype'), nullable=False, server_default='credit_p'))
    
    # Update work certificate transfers
    op.execute("""
        UPDATE transfer
        SET type = 'work_certificates'
        WHERE id IN (
            SELECT transfer_of_work_certificates
            FROM registered_hours_worked
        )
    """)
    
    # Update tax transfers
    op.execute("""
        UPDATE transfer
        SET type = 'taxes'
        WHERE id IN (
            SELECT transfer_of_taxes
            FROM registered_hours_worked
        )
    """)
    
    # Remove the server default constraint now that we've set appropriate values
    op.alter_column('transfer', 'type', server_default=None)


def downgrade() -> None:
    op.drop_column('transfer', 'type')
    
    # Drop the enum type as well
    op.execute("DROP TYPE transfertype")
