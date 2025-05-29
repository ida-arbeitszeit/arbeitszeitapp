"""Change private consumption to use transfers

Revision ID: 3c8b03a2c899
Revises: 9ab8e18b4d0e
Create Date: 2025-05-18 02:19:01.595586

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c8b03a2c899'
down_revision: Union[str, None] = '9ab8e18b4d0e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add new columns to private_consumption
    op.add_column('private_consumption', sa.Column('transfer_of_private_consumption', sa.String(), nullable=True))
    op.add_column('private_consumption', sa.Column('transfer_of_compensation', sa.String(), nullable=True))

    # 2. Add a temporary column to transfer for easier linking during migration
    op.add_column('transfer', sa.Column('temp_original_transaction_id_for_migration', sa.String(), nullable=True))

    # 3. Create main 'private_consumption' transfers and record original transaction_id
    op.execute('''
    INSERT INTO transfer (id, date, debit_account, credit_account, value, type, temp_original_transaction_id_for_migration)
    SELECT 
        gen_random_uuid()::text,
        t.date,
        t.sending_account,
        t.receiving_account,
        t.amount_sent,
        'private_consumption'::transfertype,
        t.id -- Store the original transaction_id
    FROM private_consumption pc
    JOIN transaction t ON t.id = pc.transaction_id;
    ''')

    # 4. Populate private_consumption.transfer_of_private_consumption
    op.execute('''
    UPDATE private_consumption pc
    SET transfer_of_private_consumption = t.id
    FROM transfer t
    WHERE t.temp_original_transaction_id_for_migration = pc.transaction_id
      AND t.type = 'private_consumption'::transfertype;
    ''')

    # 5. Create 'compensation' transfers and record original transaction_id
    op.execute('''
    WITH compensation_data AS (
        SELECT
            tr.id as original_transaction_id,
            tr.date as transaction_date,
            tr.amount_sent - tr.amount_received as compensation_value,
            p.planner as planner_company_id,
            pc_join.cooperation as cooperation_id
        FROM private_consumption pc_table
        JOIN transaction tr ON tr.id = pc_table.transaction_id
        JOIN plan p ON p.id = pc_table.plan_id
        JOIN plan_cooperation pc_join ON p.id = pc_join.plan
        WHERE tr.amount_sent != tr.amount_received
    )
    INSERT INTO transfer (id, date, debit_account, credit_account, value, type, temp_original_transaction_id_for_migration)
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

    # 6. Populate private_consumption.transfer_of_compensation
    op.execute('''
    UPDATE private_consumption pc
    SET transfer_of_compensation = t.id
    FROM transfer t
    WHERE t.temp_original_transaction_id_for_migration = pc.transaction_id
      AND t.type IN ('compensation_for_coop'::transfertype, 'compensation_for_company'::transfertype);
    ''')

    # 7. Drop the temporary column from transfer
    op.drop_column('transfer', 'temp_original_transaction_id_for_migration')

    # 8. Add foreign key constraints for new columns in private_consumption
    op.create_foreign_key('fk_private_consumption_transfer_pc', 'private_consumption', 'transfer', ['transfer_of_private_consumption'], ['id'])
    op.create_foreign_key('fk_private_consumption_transfer_comp', 'private_consumption', 'transfer', ['transfer_of_compensation'], ['id'])

    # 9. Make transfer_of_private_consumption not nullable
    op.alter_column('private_consumption', 'transfer_of_private_consumption', nullable=False)

    # 10. Drop old foreign key and transaction_id column from private_consumption
    op.drop_constraint('private_consumption_transaction_id_fkey', 'private_consumption', type_='foreignkey')
    op.drop_column('private_consumption', 'transaction_id')

    # 11. Delete the old transactions that were migrated to transfers
    # These transactions are now represented by entries in the 'transfer' table.
    op.execute('''
    DELETE FROM transaction t
    WHERE EXISTS (
        SELECT 1 
        FROM private_consumption pc_lookup
        JOIN transfer main_tr ON main_tr.id = pc_lookup.transfer_of_private_consumption
        WHERE main_tr.date = t.date 
          AND main_tr.debit_account = t.sending_account 
          AND main_tr.credit_account = t.receiving_account 
          AND main_tr.value = t.amount_sent
          AND main_tr.type = 'private_consumption'::transfertype 
          -- And critically, ensure this transaction was actually part of a private_consumption processed
          AND EXISTS (SELECT 1 FROM private_consumption pc_check WHERE pc_check.transfer_of_private_consumption = main_tr.id)
    );
    ''')


def downgrade() -> None:
    # 1. Add back transaction_id column to private_consumption
    op.add_column('private_consumption', sa.Column('transaction_id', sa.String(), nullable=True))

    # 2. Recreate transactions from transfers
    # The amount_received is reconstructed based on the main private consumption transfer and any compensation transfer.
    op.execute('''
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
        'Plan-Id: ' || pc.plan_id
    FROM private_consumption pc
    JOIN transfer t_pc ON t_pc.id = pc.transfer_of_private_consumption
    LEFT JOIN transfer t_comp ON t_comp.id = pc.transfer_of_compensation;
    ''')

    # 3. Populate transaction_id in private_consumption by linking to the newly created transactions
    op.execute('''
    UPDATE private_consumption pc
    SET transaction_id = t.id
    FROM transaction t, transfer t_pc
    WHERE pc.transfer_of_private_consumption = t_pc.id
      AND t.date = t_pc.date
      AND t.sending_account = t_pc.debit_account
      AND t.receiving_account = t_pc.credit_account
      AND t.amount_sent = t_pc.value;
    ''')

    # 4. Make transaction_id not nullable again
    op.alter_column('private_consumption', 'transaction_id', nullable=False)

    # 5. Add back foreign key constraint for transaction_id
    op.create_foreign_key('private_consumption_transaction_id_fkey', 'private_consumption', 'transaction', ['transaction_id'], ['id'])

    # 6. Drop foreign key constraints for transfer columns on private_consumption FIRST
    # These constraints prevent the deletion of transfers if they are still referenced.
    op.drop_constraint('fk_private_consumption_transfer_comp', 'private_consumption', type_='foreignkey')
    op.drop_constraint('fk_private_consumption_transfer_pc', 'private_consumption', type_='foreignkey')

    # 7. Delete the transfers that were created by the upgrade.
    op.execute('''
    DELETE FROM transfer t
    WHERE t.id IN (
        SELECT transfer_of_compensation 
        FROM private_consumption 
        WHERE transfer_of_compensation IS NOT NULL
    );
    ''')
    op.execute('''
    DELETE FROM transfer t
    WHERE t.id IN (
        SELECT transfer_of_private_consumption 
        FROM private_consumption 
        WHERE transfer_of_private_consumption IS NOT NULL
    );
    ''')
    
    # 8. Drop transfer-related columns from private_consumption
    op.drop_column('private_consumption', 'transfer_of_compensation')
    op.drop_column('private_consumption', 'transfer_of_private_consumption')
