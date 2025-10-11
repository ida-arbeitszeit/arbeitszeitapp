"""Add explicit account keys to company table

Revision ID: 52e3a1f4fc9a
Revises: 5517f6309552
Create Date: 2023-01-04 11:59:37.940015

"""
from alembic import op
import sqlalchemy as sa
import enum


# revision identifiers, used by Alembic.
revision = '52e3a1f4fc9a'
down_revision = '5517f6309552'
branch_labels = None
depends_on = None

class AccountType(enum.Enum):
    p = "p"
    r = "r"
    a = "a"
    prd = "prd"
    member = "member"
    accounting = "accounting"


def upgrade():
    op.add_column('company', sa.Column('p_account', sa.String()))
    op.add_column('company', sa.Column('r_account', sa.String()))
    op.add_column('company', sa.Column('a_account', sa.String()))
    op.add_column('company', sa.Column('prd_account', sa.String()))
    with op.batch_alter_table('company') as batch_op:
        batch_op.create_foreign_key('company_r_account_fkey', 'account', ['r_account'], ['id'])
        batch_op.create_foreign_key('company_a_account_fkey', 'account', ['a_account'], ['id'])
        batch_op.create_foreign_key('company_p_account_fkey', 'account', ['p_account'], ['id'])
        batch_op.create_foreign_key('company_prd_account_fkey', 'account', ['prd_account'], ['id'])
    op.execute(
        """
        UPDATE company
        SET p_account = (
            SELECT id
            FROM account
            WHERE company.id = account.account_owner_company
                AND account.account_type = 'p'
        )
        """
    )
    op.execute(
        """
        UPDATE company
        SET r_account = (
            SELECT id
            FROM account
            WHERE company.id = account.account_owner_company
                AND account.account_type = 'r'
        )
        """
    )
    op.execute(
        """
        UPDATE company
        SET a_account = (
            SELECT id
            FROM account
            WHERE company.id = account.account_owner_company
                AND account.account_type = 'a'
        )
        """
    )
    op.execute(
        """
        UPDATE company
        SET prd_account = (
            SELECT id
            FROM account
            WHERE company.id = account.account_owner_company
                AND account.account_type = 'prd'
        )
        """
    )
    with op.batch_alter_table('account') as batch_op:
        batch_op.drop_constraint('account_account_owner_company_fkey', type_='foreignkey')
    op.drop_column('account', 'account_owner_company')
    with op.batch_alter_table('company') as batch_op:
        batch_op.alter_column('p_account',
                   existing_type=sa.VARCHAR(),
                   nullable=False)
        batch_op.alter_column('r_account',
                   existing_type=sa.VARCHAR(),
                   nullable=False)
        batch_op.alter_column('a_account',
                   existing_type=sa.VARCHAR(),
                   nullable=False)
        batch_op.alter_column('prd_account',
                   existing_type=sa.VARCHAR(),
                   nullable=False)


def downgrade():
    with op.batch_alter_table('company') as batch_op:
        batch_op.alter_column('prd_account',
                   existing_type=sa.VARCHAR(),
                   nullable=True)
        batch_op.alter_column('a_account',
                   existing_type=sa.VARCHAR(),
                   nullable=True)
        batch_op.alter_column('r_account',
                   existing_type=sa.VARCHAR(),
                   nullable=True)
        batch_op.alter_column('p_account',
                   existing_type=sa.VARCHAR(),
                   nullable=True)
    op.add_column('account', sa.Column('account_owner_company', sa.String()))
    with op.batch_alter_table('account') as batch_op:
        batch_op.create_foreign_key('account_account_owner_company_fkey', 'company', ['account_owner_company'], ['id'])
    op.execute(
        """
        UPDATE account
        SET account_owner_company = (
            SELECT id
            FROM company
            WHERE company.p_account = account.id
                OR company.r_account = account.id
                OR company.a_account = account.id
                OR company.prd_account = account.id
        )
        """
    )
    with op.batch_alter_table('company') as batch_op:
        batch_op.drop_constraint('company_prd_account_fkey', type_='foreignkey')
        batch_op.drop_constraint('company_a_account_fkey', type_='foreignkey')
        batch_op.drop_constraint('company_r_account_fkey', type_='foreignkey')
        batch_op.drop_constraint('company_p_account_fkey', type_='foreignkey')
    op.drop_column('company', 'prd_account')
    op.drop_column('company', 'a_account')
    op.drop_column('company', 'r_account')
    op.drop_column('company', 'p_account')
