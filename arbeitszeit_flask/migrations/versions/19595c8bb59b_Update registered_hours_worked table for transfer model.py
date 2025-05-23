"""Update registered_hours_worked table for transfer model

Revision ID: 19595c8bb59b
Revises: 2f097be4f4d2
Create Date: 2025-03-20 21:39:13.101345

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from uuid import uuid4


revision: str = '19595c8bb59b'
down_revision: Union[str, None] = '2f097be4f4d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add new transfer columns
    op.add_column('registered_hours_worked',
        sa.Column('transfer_of_work_certificates', sa.String(), nullable=True)
    )
    op.add_column('registered_hours_worked',
        sa.Column('transfer_of_taxes', sa.String(), nullable=True)
    )
    
    # Add foreign key constraints
    op.create_foreign_key(
        'fk_registered_hours_worked_transfer_work_certificates',
        'registered_hours_worked', 'transfer',
        ['transfer_of_work_certificates'], ['id']
    )
    op.create_foreign_key(
        'fk_registered_hours_worked_transfer_taxes',
        'registered_hours_worked', 'transfer',
        ['transfer_of_taxes'], ['id']
    )

    # First, create a temporary table to store the transfer IDs
    op.execute('''
    CREATE TEMP TABLE transfer_mapping AS
    WITH existing_data AS (
        SELECT 
            rhw.id as rhw_id,
            t.date,
            t.sending_account as company_a_account,
            t.receiving_account as member_account,
            t.amount_sent as hours_worked,
            CASE 
                WHEN t.amount_sent = 0 THEN 0
                ELSE (t.amount_sent - t.amount_received) / t.amount_sent
            END as tax_rate,
            sa.account_psf as psf_account
        FROM registered_hours_worked rhw
        JOIN transaction t ON t.id = rhw.transaction
        CROSS JOIN social_accounting sa
    )
    SELECT 
        ed.rhw_id,
        gen_random_uuid()::text as work_certificate_transfer_id,
        gen_random_uuid()::text as tax_transfer_id,
        ed.date,
        ed.company_a_account,
        ed.member_account,
        ed.hours_worked,
        ed.tax_rate,
        ed.psf_account
    FROM existing_data ed;
    ''')

    # Insert the transfers
    op.execute('''
    INSERT INTO transfer (id, date, debit_account, credit_account, value)
    SELECT 
        work_certificate_transfer_id,
        date,
        company_a_account,
        member_account,
        hours_worked
    FROM transfer_mapping;
    ''')

    op.execute('''
    INSERT INTO transfer (id, date, debit_account, credit_account, value)
    SELECT 
        tax_transfer_id,
        date,
        company_a_account,
        psf_account,
        hours_worked * tax_rate
    FROM transfer_mapping;
    ''')

    # Update the registered_hours_worked table with the new transfer IDs
    op.execute('''
    UPDATE registered_hours_worked rhw
    SET 
        transfer_of_work_certificates = tm.work_certificate_transfer_id,
        transfer_of_taxes = tm.tax_transfer_id
    FROM transfer_mapping tm
    WHERE rhw.id = tm.rhw_id;
    ''')

    # Drop the temporary table
    op.execute('DROP TABLE transfer_mapping;')

    # Make transfer columns not nullable after migration
    op.alter_column('registered_hours_worked', 'transfer_of_work_certificates',
        nullable=False
    )
    op.alter_column('registered_hours_worked', 'transfer_of_taxes',
        nullable=False
    )

    # Drop old transaction column and its foreign key
    op.drop_constraint(
        'registered_hours_worked_transaction_fkey',
        'registered_hours_worked',
        type_='foreignkey'
    )
    op.drop_column('registered_hours_worked', 'transaction')

    # Remove the redundant amount column
    op.drop_column('registered_hours_worked', 'amount')

def downgrade():
    # Add back transaction and amount columns
    op.add_column('registered_hours_worked',
        sa.Column('transaction', sa.String(), nullable=True)
    )
    op.add_column('registered_hours_worked',
        sa.Column('amount', sa.Numeric(), nullable=True)  
    )

    # Create temporary table for mapping transfer data to transactions
    op.execute('''
    CREATE TEMP TABLE transaction_mapping AS
    SELECT 
        rhw.id as rhw_id,
        gen_random_uuid()::text as transaction_id,
        wct.date,
        wct.debit_account as sending_account,
        wct.credit_account as receiving_account,
        wct.value as amount_sent,
        wct.value - tt.value as amount_received
    FROM registered_hours_worked rhw
    JOIN transfer wct ON wct.id = rhw.transfer_of_work_certificates
    JOIN transfer tt ON tt.id = rhw.transfer_of_taxes;
    ''')

    # Insert mapped data into transactions table 
    op.execute('''
    INSERT INTO transaction (
        id, date, sending_account, receiving_account, 
        amount_sent, amount_received, purpose
    )
    SELECT 
        transaction_id,
        date,
        sending_account,
        receiving_account,
        amount_sent,
        amount_received,
        'Lohn'
    FROM transaction_mapping;
    ''')

    # Update registered_hours_worked with transaction IDs and amounts
    op.execute('''
    UPDATE registered_hours_worked rhw
    SET 
        transaction = tm.transaction_id,
        amount = tm.amount_sent
    FROM transaction_mapping tm
    WHERE rhw.id = tm.rhw_id;
    ''')

    # Make transaction and amount columns NOT NULL
    op.alter_column('registered_hours_worked', 'transaction', nullable=False)
    op.alter_column('registered_hours_worked', 'amount', nullable=False)

    # Add back foreign key constraint to transaction
    op.create_foreign_key(
        'registered_hours_worked_transaction_fkey',
        'registered_hours_worked', 'transaction',
        ['transaction'], ['id']
    )

    # Drop the foreign key constraints to transfer columns
    op.drop_constraint(
        'fk_registered_hours_worked_transfer_work_certificates',
        'registered_hours_worked',
        type_='foreignkey'
    )
    op.drop_constraint(
        'fk_registered_hours_worked_transfer_taxes',
        'registered_hours_worked',
        type_='foreignkey'
    )

    # Delete the transfers that were migrated
    op.execute('''
    DELETE FROM transfer 
    WHERE id IN (
        SELECT transfer_of_work_certificates 
        FROM registered_hours_worked
        UNION
        SELECT transfer_of_taxes
        FROM registered_hours_worked
    );
    ''')

    # Drop the temporary mapping table
    op.execute('DROP TABLE transaction_mapping;')

    # Drop the transfer columns
    op.drop_column('registered_hours_worked', 'transfer_of_work_certificates')
    op.drop_column('registered_hours_worked', 'transfer_of_taxes')
