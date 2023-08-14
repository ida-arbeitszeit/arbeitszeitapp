"""rename table consumer_purchase to private_consumption

Revision ID: 888f16f6528d
Revises: c917f02f0e95
Create Date: 2023-08-14 20:05:58.837517

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '888f16f6528d'
down_revision = 'c917f02f0e95'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(constraint_name="consumer_purchase_plan_id_fkey", table_name="consumer_purchase", type_="foreignkey")
    op.drop_constraint(constraint_name="consumer_purchase_transaction_id_fkey", table_name="consumer_purchase", type_="foreignkey")
    op.rename_table("consumer_purchase", "private_consumption")
    op.execute('ALTER INDEX consumer_purchase_pkey RENAME TO private_consumption_pkey')
    op.create_foreign_key("private_consumption_plan_id_fkey", "private_consumption", "plan", ["plan_id"], ["id"])
    op.create_foreign_key("private_consumption_transaction_id_fkey", "private_consumption", "transaction", ["transaction_id"], ["id"])
    
def downgrade():
    op.drop_constraint(constraint_name="private_consumption_plan_id_fkey", table_name="private_consumption", type_="foreignkey")
    op.drop_constraint(constraint_name="private_consumption_transaction_id_fkey", table_name="private_consumption", type_="foreignkey")
    op.rename_table("private_consumption", "consumer_purchase")
    op.execute('ALTER INDEX private_consumption_pkey RENAME TO consumer_purchase_pkey')
    op.create_foreign_key("consumer_purchase_plan_id_fkey", "consumer_purchase", "plan", ["plan_id"], ["id"])
    op.create_foreign_key("consumer_purchase_transaction_id_fkey", "consumer_purchase", "transaction", ["transaction_id"], ["id"])
    
    
    