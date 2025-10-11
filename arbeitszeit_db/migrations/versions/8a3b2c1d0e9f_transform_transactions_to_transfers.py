"""Transform transactions to transfers and create plan_approval table

Revision ID: 8a3b2c1d0e9f
Revises: 0f1f3b156d62
Create Date: 2024-05-04 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm
from uuid import uuid4


# revision identifiers, used by Alembic.
revision: str = '8a3b2c1d0e9f'
down_revision: Union[str, None] = '0f1f3b156d62'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create plan_approval table
    op.create_table(
        'plan_approval',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('plan_id', sa.String(), nullable=False),
        sa.Column('date', sa.DateTime(), nullable=False),
        sa.Column('transfer_of_credit_p', sa.String(), nullable=False),
        sa.Column('transfer_of_credit_r', sa.String(), nullable=False),
        sa.Column('transfer_of_credit_a', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['plan.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['transfer_of_credit_p'], ['transfer.id']),
        sa.ForeignKeyConstraint(['transfer_of_credit_r'], ['transfer.id']),
        sa.ForeignKeyConstraint(['transfer_of_credit_a'], ['transfer.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # First delete transactions that have SocialAccounting.account as sender and Plan-Id: purpose
    # but have a company's prd_account as receiver
    op.execute('''
    DELETE FROM transaction t
    WHERE EXISTS (
        SELECT 1 FROM social_accounting sa
        WHERE sa.account = t.sending_account
        AND t.purpose LIKE 'Plan-Id: %'
    )
    AND EXISTS (
        SELECT 1 FROM company c
        WHERE c.prd_account = t.receiving_account
    );
    ''')

    # Create temporary table to store plan-related transfers
    op.execute('''
    CREATE TEMP TABLE plan_transfers AS
    WITH plan_transactions AS (
        SELECT 
            t.id as transaction_id,
            t.date,
            t.sending_account,
            t.receiving_account,
            t.amount_sent,
            t.purpose,
            p.id as plan_id,
            p.is_public_service,
            c.id as company_id,
            c.p_account,
            c.r_account,
            c.a_account,
            c.prd_account,
            sa.account_psf
        FROM transaction t
        JOIN social_accounting sa ON sa.account = t.sending_account
        JOIN plan p ON p.id = SUBSTRING(t.purpose FROM 'Plan-Id: ([0-9a-f-]+)')
        JOIN company c ON t.receiving_account IN (c.p_account, c.r_account, c.a_account)
        WHERE t.purpose LIKE 'Plan-Id: %'
    )
    SELECT 
        pt.transaction_id,
        pt.date,
        pt.plan_id,
        pt.is_public_service,
        pt.company_id,
        CASE 
            WHEN pt.receiving_account = pt.p_account THEN 'p'
            WHEN pt.receiving_account = pt.r_account THEN 'r'
            WHEN pt.receiving_account = pt.a_account THEN 'a'
        END as account_type,
        CASE 
            WHEN pt.is_public_service THEN pt.account_psf
            ELSE pt.prd_account
        END as debit_account,
        pt.receiving_account as credit_account,
        pt.amount_sent as value,
        CASE 
            WHEN pt.is_public_service THEN 
                CASE 
                    WHEN pt.receiving_account = pt.p_account THEN 'credit_public_p'
                    WHEN pt.receiving_account = pt.r_account THEN 'credit_public_r'
                    WHEN pt.receiving_account = pt.a_account THEN 'credit_public_a'
                END
            ELSE 
                CASE 
                    WHEN pt.receiving_account = pt.p_account THEN 'credit_p'
                    WHEN pt.receiving_account = pt.r_account THEN 'credit_r'
                    WHEN pt.receiving_account = pt.a_account THEN 'credit_a'
                END
        END as transfer_type
    FROM plan_transactions pt;
    ''')

    # Insert transfers from plan transactions
    op.execute('''
    INSERT INTO transfer (id, date, debit_account, credit_account, value, type)
    SELECT 
        gen_random_uuid()::text,
        date,
        debit_account,
        credit_account,
        value,
        transfer_type::transfertype
    FROM plan_transfers;
    ''')

    # Create plan approvals
    op.execute('''
    INSERT INTO plan_approval (id, plan_id, date, transfer_of_credit_p, transfer_of_credit_r, transfer_of_credit_a)
    SELECT 
        gen_random_uuid()::text,
        pt.plan_id,
        pr.approval_date,
        MAX(CASE WHEN pt.account_type = 'p' THEN t.id END),
        MAX(CASE WHEN pt.account_type = 'r' THEN t.id END),
        MAX(CASE WHEN pt.account_type = 'a' THEN t.id END)
    FROM plan_transfers pt
    JOIN transfer t ON 
        t.date = pt.date AND
        t.debit_account = pt.debit_account AND
        t.credit_account = pt.credit_account AND
        t.value = pt.value AND
        t.type::text = pt.transfer_type
    JOIN plan_review pr ON pr.plan_id = pt.plan_id
    GROUP BY pt.plan_id, pr.approval_date;
    ''')

    # Drop the temporary table
    op.execute('DROP TABLE plan_transfers;')

    # Delete transactions that were transformed to transfers
    op.execute('''
    DELETE FROM transaction t
    WHERE EXISTS (
        SELECT 1 FROM social_accounting sa
        WHERE sa.account = t.sending_account
        AND t.purpose LIKE 'Plan-Id: %'
    );
    ''')

    # Drop PlanReview.approval_date column
    op.drop_column('plan_review', 'approval_date')


def downgrade() -> None:
    # Add back PlanReview.approval_date column
    op.add_column('plan_review', sa.Column('approval_date', sa.DateTime(), nullable=True))

    # Restore approval dates from plan_approval table
    op.execute('''
    UPDATE plan_review pr
    SET approval_date = pa.date
    FROM plan_approval pa
    WHERE pr.plan_id = pa.plan_id;
    ''')

    # Drop plan_approval table
    op.drop_table('plan_approval')

    # Note: We cannot restore the original transactions since we don't have enough information
    # to reconstruct them exactly as they were. The downgrade will leave the database in a
    # state where these transactions are missing. 