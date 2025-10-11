"""rename table company_purchase

Revision ID: c56e8291e74d
Revises: 888f16f6528d
Create Date: 2023-08-22 16:14:01.814994

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c56e8291e74d'
down_revision = '888f16f6528d'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(constraint_name="company_purchase_plan_id_fkey", table_name="company_purchase", type_="foreignkey")
    op.drop_constraint(constraint_name="company_purchase_transaction_id_fkey", table_name="company_purchase", type_="foreignkey")
    op.rename_table("company_purchase", "productive_consumption")
    op.execute('ALTER INDEX company_purchase_pkey RENAME TO productive_consumption_pkey')
    op.create_foreign_key("productive_consumption_plan_id_fkey", "productive_consumption", "plan", ["plan_id"], ["id"])
    op.create_foreign_key("productive_consumption_transaction_id_fkey", "productive_consumption", "transaction", ["transaction_id"], ["id"])
    
def downgrade():
    op.drop_constraint(constraint_name="productive_consumption_plan_id_fkey", table_name="productive_consumption", type_="foreignkey")
    op.drop_constraint(constraint_name="productive_consumption_transaction_id_fkey", table_name="productive_consumption", type_="foreignkey")
    op.rename_table("productive_consumption", "company_purchase")
    op.execute('ALTER INDEX productive_consumption_pkey RENAME TO company_purchase_pkey')
    op.create_foreign_key("company_purchase_plan_id_fkey", "company_purchase", "plan", ["plan_id"], ["id"])
    op.create_foreign_key("company_purchase_transaction_id_fkey", "company_purchase", "transaction", ["transaction_id"], ["id"])
    
