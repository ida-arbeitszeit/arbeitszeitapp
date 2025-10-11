# type: ignore
"""empty message

Revision ID: 15d33dfe8ec7
Revises: 2185d9d4448f
Create Date: 2023-02-15 13:04:28.046515

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm
from uuid import UUID


# revision identifiers, used by Alembic.
revision = '15d33dfe8ec7'
down_revision = '2185d9d4448f'
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'labour_certificates_payout',
        sa.Column('transaction_id', sa.String(), nullable=False),
        sa.Column('plan_id', sa.String(), nullable=False),
        sa.ForeignKeyConstraint(['plan_id'], ['plan.id'], ),
        sa.ForeignKeyConstraint(['transaction_id'], ['transaction.id'], ),
        sa.PrimaryKeyConstraint('transaction_id')
    )
    bind = op.get_bind()
    with orm.Session(bind=bind) as session:
        certificate_payout_transactions = session.query(Transaction).filter(
            sa.and_(
                Transaction.sending_account.in_(
                    session.query(SocialAccounting).with_entities(SocialAccounting.account)
                ),
                Transaction.receiving_account.in_(
                    session.query(Company).with_entities(Company.a_account)
                )
            )
        )
        for transaction in certificate_payout_transactions:
            plan_id = transaction.purpose.removeprefix("Plan-Id: ")
            UUID(plan_id)
            payout = LabourCertificatesPayout(
                transaction_id=transaction.id,
                plan_id=plan_id,
            )
            session.add(payout)
        session.commit()
    with op.batch_alter_table('plan', schema=None) as batch_op:
        batch_op.drop_column('payout_count')


def downgrade():
    with op.batch_alter_table('plan', schema=None) as batch_op:
        batch_op.add_column(sa.Column('payout_count', sa.INTEGER(), autoincrement=False, nullable=True))
    bind = op.get_bind()
    with orm.Session(bind=bind) as session:
        for plan in session.query(Plan):
            payout_count = session.query(LabourCertificatesPayout).filter(LabourCertificatesPayout.plan_id == plan.id).count()
            plan.payout_count = payout_count
        session.commit()
    with op.batch_alter_table('plan') as batch_op:
        batch_op.alter_column(sa.Column('payout_count', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_table('labour_certificates_payout')


Base = orm.declarative_base()


class Company(Base):
    __tablename__ = "company"

    id = sa.Column(sa.String, primary_key=True)
    a_account = sa.Column(sa.ForeignKey("account.id"), nullable=False)


class SocialAccounting(Base):
    __tablename__ = "social_accounting"
    id = sa.Column(sa.String, primary_key=True)
    account = sa.Column(sa.ForeignKey("account.id"), nullable=False)


class Transaction(Base):
    __tablename__ = "transaction"
    id = sa.Column(
        sa.String,
        primary_key=True,
    )
    date = sa.Column(sa.DateTime, nullable=False)
    sending_account = sa.Column(
        sa.String,
        sa.ForeignKey("account.id"),
        nullable=False
    )
    receiving_account = sa.Column(
        sa.String,
        sa.ForeignKey("account.id"),
        nullable=False,
    )
    purpose = sa.Column(sa.String(1000), nullable=True)


class LabourCertificatesPayout(Base):
    __tablename__ = "labour_certificates_payout"
    transaction_id = sa.Column(
        sa.String,
        sa.ForeignKey("transaction.id"),
        nullable=False,
        primary_key=True,
    )
    plan_id = sa.Column(sa.String, sa.ForeignKey("plan.id"), nullable=False)


class Plan(Base):
    __tablename__ = "plan"
    id = sa.Column(sa.String, primary_key=True)
    payout_count = sa.Column(sa.Integer, nullable=False, default=0)
