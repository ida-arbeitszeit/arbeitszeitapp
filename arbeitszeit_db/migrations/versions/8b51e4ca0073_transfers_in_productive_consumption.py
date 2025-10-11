"""transfers in productive consumption

Revision ID: 8b51e4ca0073
Revises: 3c8b03a2c899
Create Date: 2025-06-02 13:21:31.013768

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '8b51e4ca0073'
down_revision: Union[str, None] = '3c8b03a2c899'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add new columns to productive_consumption
    op.add_column('productive_consumption', sa.Column('transfer_of_productive_consumption', sa.String(), nullable=True))
    op.add_column('productive_consumption', sa.Column('transfer_of_compensation', sa.String(), nullable=True))

    # 2. Add a temporary column to transfer for easier linking during migration
    op.add_column('transfer', sa.Column('temp_original_transaction_id_for_migration_pc', sa.String(), nullable=True)) # Suffix pc to avoid conflict if run in same transaction as other migration

    # 3. Create main 'productive_consumption_p/r' transfers and record original transaction_id
    op.execute(f'''
    INSERT INTO transfer (id, date, debit_account, credit_account, value, type, temp_original_transaction_id_for_migration_pc)
    SELECT 
        gen_random_uuid()::text,
        t.date,
        t.sending_account,
        t.receiving_account,
        t.amount_sent,
        CASE
            WHEN t.sending_account = c.p_account THEN 'productive_consumption_p'::transfertype
            WHEN t.sending_account = c.r_account THEN 'productive_consumption_r'::transfertype
            ELSE NULL -- Should not happen if data is consistent
        END,
        t.id -- Store the original transaction_id
    FROM productive_consumption prod_c
    JOIN transaction t ON t.id = prod_c.transaction_id
    JOIN company c ON (t.sending_account = c.p_account OR t.sending_account = c.r_account) -- Assuming sending_account belongs to a company
    WHERE CASE
            WHEN t.sending_account = c.p_account THEN 'productive_consumption_p'::transfertype
            WHEN t.sending_account = c.r_account THEN 'productive_consumption_r'::transfertype
            ELSE NULL
          END IS NOT NULL;
    ''')

    # 4. Populate productive_consumption.transfer_of_productive_consumption
    op.execute(f'''
    UPDATE productive_consumption prod_c
    SET transfer_of_productive_consumption = tr.id
    FROM transfer tr
    WHERE tr.temp_original_transaction_id_for_migration_pc = prod_c.transaction_id
      AND tr.type IN ('productive_consumption_p'::transfertype, 'productive_consumption_r'::transfertype);
    ''')

    # 5. Create 'compensation' transfers and record original transaction_id
    op.execute(f'''
    WITH compensation_data AS (
        SELECT
            tr.id as original_transaction_id,
            tr.date as transaction_date,
            tr.amount_sent - tr.amount_received as compensation_value,
            p.planner as planner_company_id,
            pc_join.cooperation as cooperation_id
        FROM productive_consumption prod_c_table
        JOIN transaction tr ON tr.id = prod_c_table.transaction_id
        JOIN plan p ON p.id = prod_c_table.plan_id
        JOIN plan_cooperation pc_join ON p.id = pc_join.plan
        WHERE tr.amount_sent != tr.amount_received
    )
    INSERT INTO transfer (id, date, debit_account, credit_account, value, type, temp_original_transaction_id_for_migration_pc)
    SELECT
        gen_random_uuid()::text,
        cd.transaction_date,
        CASE
            WHEN cd.compensation_value > 0 THEN comp.prd_account -- compensation_for_coop: company prd_account is debit
            ELSE coop.account -- compensation_for_company: cooperation account is debit
        END,
        CASE
            WHEN cd.compensation_value > 0 THEN coop.account -- compensation_for_coop: cooperation account is credit
            ELSE comp.prd_account -- compensation_for_company: company prd_account is credit
        END,
        abs(cd.compensation_value),
        CASE
            WHEN cd.compensation_value > 0 THEN 'compensation_for_coop'::transfertype
            ELSE 'compensation_for_company'::transfertype
        END,
        cd.original_transaction_id -- Store the original transaction_id
    FROM compensation_data cd
    JOIN company comp ON comp.id = cd.planner_company_id
    JOIN cooperation coop ON coop.id = cd.cooperation_id;
    ''')

    # 6. Populate productive_consumption.transfer_of_compensation
    op.execute(f'''
    UPDATE productive_consumption prod_c
    SET transfer_of_compensation = tr.id
    FROM transfer tr
    WHERE tr.temp_original_transaction_id_for_migration_pc = prod_c.transaction_id
      AND tr.type IN ('compensation_for_coop'::transfertype, 'compensation_for_company'::transfertype);
    ''')

    # 7. Drop the temporary column from transfer
    op.drop_column('transfer', 'temp_original_transaction_id_for_migration_pc')

    # 8. Add foreign key constraints for new columns in productive_consumption
    op.create_foreign_key('fk_productive_consumption_transfer_pc', 'productive_consumption', 'transfer', ['transfer_of_productive_consumption'], ['id'])
    op.create_foreign_key('fk_productive_consumption_transfer_comp', 'productive_consumption', 'transfer', ['transfer_of_compensation'], ['id'])

    # 9. Make transfer_of_productive_consumption not nullable
    op.alter_column('productive_consumption', 'transfer_of_productive_consumption', nullable=False)

    # 10. Drop old foreign key and transaction_id column from productive_consumption
    op.drop_constraint('productive_consumption_transaction_id_fkey', 'productive_consumption', type_='foreignkey')
    op.drop_column('productive_consumption', 'transaction_id')

    # 11. Delete the old transactions that were migrated to transfers
    op.execute(f'''
    DELETE FROM transaction t
    WHERE EXISTS (
        SELECT 1 
        FROM productive_consumption pc_lookup
        JOIN transfer main_tr ON main_tr.id = pc_lookup.transfer_of_productive_consumption
        WHERE main_tr.date = t.date 
          AND main_tr.debit_account = t.sending_account 
          AND main_tr.credit_account = t.receiving_account 
          AND main_tr.value = t.amount_sent
          AND main_tr.type IN ('productive_consumption_p'::transfertype, 'productive_consumption_r'::transfertype)
          AND EXISTS (SELECT 1 FROM productive_consumption pc_check WHERE pc_check.transfer_of_productive_consumption = main_tr.id AND pc_check.id = pc_lookup.id)
    );
    ''')


def downgrade() -> None:
    # 1. Add back transaction_id column to productive_consumption
    op.add_column('productive_consumption', sa.Column('transaction_id', sa.String(), nullable=True))

    # 2. Recreate transactions from transfers
    # This needs to map 'productive_consumption_p' and 'productive_consumption_r' back.
    # The amount_received is reconstructed based on the main productive consumption transfer and any compensation transfer.
    op.execute(f'''
    INSERT INTO transaction (id, date, sending_account, receiving_account, amount_sent, amount_received, purpose)
    SELECT 
        gen_random_uuid()::text,
        t_pc.date,
        t_pc.debit_account,
        t_pc.credit_account,
        t_pc.value, -- This is the original amount_sent
        CASE
            WHEN t_comp.id IS NOT NULL AND t_comp.type = 'compensation_for_coop'::transfertype THEN t_pc.value - t_comp.value
            WHEN t_comp.id IS NOT NULL AND t_comp.type = 'compensation_for_company'::transfertype THEN t_pc.value + t_comp.value
            ELSE t_pc.value -- No compensation, so amount_received = amount_sent
        END as amount_received,
        'Plan-Id: ' || prod_c.plan_id
    FROM productive_consumption prod_c
    JOIN transfer t_pc ON t_pc.id = prod_c.transfer_of_productive_consumption
    LEFT JOIN transfer t_comp ON t_comp.id = prod_c.transfer_of_compensation
    WHERE t_pc.type IN ('productive_consumption_p'::transfertype, 'productive_consumption_r'::transfertype);
    ''')

    # 3. Populate transaction_id in productive_consumption by linking to the newly created transactions
    op.execute(f'''
    UPDATE productive_consumption prod_c
    SET transaction_id = t.id
    FROM transaction t, transfer t_pc
    WHERE prod_c.transfer_of_productive_consumption = t_pc.id
      AND t.date = t_pc.date
      AND t.sending_account = t_pc.debit_account
      AND t.receiving_account = t_pc.credit_account
      AND t.amount_sent = t_pc.value
      AND t_pc.type IN ('productive_consumption_p'::transfertype, 'productive_consumption_r'::transfertype)
      AND ('Plan-Id: ' || prod_c.plan_id) = t.purpose; -- Added purpose matching for more accuracy
    ''')

    # 4. Make transaction_id not nullable again
    op.alter_column('productive_consumption', 'transaction_id', nullable=False)

    # 5. Add back foreign key constraint for transaction_id
    op.create_foreign_key('productive_consumption_transaction_id_fkey', 'productive_consumption', 'transaction', ['transaction_id'], ['id'])

    # 6. Drop foreign key constraints for transfer columns on productive_consumption FIRST
    op.drop_constraint('fk_productive_consumption_transfer_comp', 'productive_consumption', type_='foreignkey')
    op.drop_constraint('fk_productive_consumption_transfer_pc', 'productive_consumption', type_='foreignkey')

    # 7. Delete the transfers that were created by the upgrade.
    op.execute(f'''
    DELETE FROM transfer t
    WHERE t.id IN (
        SELECT transfer_of_compensation 
        FROM productive_consumption 
        WHERE transfer_of_compensation IS NOT NULL
    ) AND t.type IN ('compensation_for_coop'::transfertype, 'compensation_for_company'::transfertype);
    ''')
    op.execute(f'''
    DELETE FROM transfer t
    WHERE t.id IN (
        SELECT transfer_of_productive_consumption 
        FROM productive_consumption 
        WHERE transfer_of_productive_consumption IS NOT NULL
    ) AND t.type IN ('productive_consumption_p'::transfertype, 'productive_consumption_r'::transfertype);
    ''')
    
    # 8. Drop transfer-related columns from productive_consumption
    op.drop_column('productive_consumption', 'transfer_of_compensation')
    op.drop_column('productive_consumption', 'transfer_of_productive_consumption')
