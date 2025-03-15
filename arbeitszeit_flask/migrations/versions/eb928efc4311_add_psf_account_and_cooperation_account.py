"""Add PSF account and Cooperation account

Revision ID: eb928efc4311
Revises: e0cb944a36b2
Create Date: 2025-03-15 00:30:26.896982

"""
from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import Session


# revision identifiers, used by Alembic.
revision: str = 'eb928efc4311'
down_revision: Union[str, None] = 'e0cb944a36b2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


Base = orm.declarative_base()

# Define models for use in the migration
class Account(Base):
    __tablename__ = "account"
    id = sa.Column(sa.String, primary_key=True)

class SocialAccounting(Base):
    __tablename__ = "social_accounting"
    id = sa.Column(sa.String, primary_key=True)
    account = sa.Column(sa.String, sa.ForeignKey("account.id"))
    account_psf = sa.Column(sa.String, sa.ForeignKey("account.id"), nullable=True)

class Cooperation(Base):
    __tablename__ = "cooperation"
    id = sa.Column(sa.String, primary_key=True)
    creation_date = sa.Column(sa.DateTime)
    name = sa.Column(sa.String(100))
    definition = sa.Column(sa.String(5000))
    account = sa.Column(sa.String, sa.ForeignKey("account.id"), nullable=True)


def upgrade():
    # Step 1: Add columns as nullable initially
    op.add_column('social_accounting', sa.Column('account_psf', sa.String(), nullable=True))
    op.create_foreign_key(
        'fk_social_accounting_account_psf', 
        'social_accounting', 'account', 
        ['account_psf'], ['id']
    )
    
    op.add_column('cooperation', sa.Column('account', sa.String(), nullable=True))
    op.create_foreign_key(
        'fk_cooperation_account', 
        'cooperation', 'account', 
        ['account'], ['id']
    )
    
    # Step 2: Create and assign accounts
    bind = op.get_bind()
    session = Session(bind=bind)
    
    try:
        # Create PSF account for social accounting
        social_accounting = session.query(SocialAccounting).first()
        if social_accounting and not social_accounting.account_psf:
            psf_account_id = str(uuid4())
            # Insert new account
            session.execute(
                sa.text("INSERT INTO account (id) VALUES (:id)"),
                {"id": psf_account_id}
            )
            # Update social accounting with PSF account
            session.execute(
                sa.text("UPDATE social_accounting SET account_psf = :psf_account_id WHERE id = :sa_id"),
                {"psf_account_id": psf_account_id, "sa_id": social_accounting.id}
            )
            print(f"Created PSF account {psf_account_id} for social accounting")
        
        # Create accounts for all cooperations
        cooperations = session.query(Cooperation).all()
        for cooperation in cooperations:
            if not cooperation.account:
                coop_account_id = str(uuid4())
                # Insert new account
                session.execute(
                    sa.text("INSERT INTO account (id) VALUES (:id)"),
                    {"id": coop_account_id}
                )
                # Update cooperation with account
                session.execute(
                    sa.text("UPDATE cooperation SET account = :account_id WHERE id = :coop_id"),
                    {"account_id": coop_account_id, "coop_id": cooperation.id}
                )
                print(f"Created account {coop_account_id} for cooperation {cooperation.name} ({cooperation.id})")
        
        session.commit()
        print("Account initialization completed")
    except Exception as e:
        session.rollback()
        print(f"Error during migration: {e}")
        raise
    finally:
        session.close()

    # Step 3: Alter columns to be non-nullable
    op.alter_column('social_accounting', 'account_psf', nullable=False)
    op.alter_column('cooperation', 'account', nullable=False)

def downgrade():
    # First make columns nullable again
    op.alter_column('social_accounting', 'account_psf', nullable=True)
    op.alter_column('cooperation', 'account', nullable=True)
    
    # Remove foreign key constraints
    op.drop_constraint('fk_social_accounting_account_psf', 'social_accounting', type_='foreignkey')
    op.drop_constraint('fk_cooperation_account', 'cooperation', type_='foreignkey')
    
    # Then remove columns
    op.drop_column('social_accounting', 'account_psf')
    op.drop_column('cooperation', 'account')