"""Create registered_hours_worked table

Revision ID: 8245d6c57ca5
Revises: 51b2f780aba4
Create Date: 2024-06-03 18:17:20.397152

"""

from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy import orm

revision = "8245d6c57ca5"
down_revision = "51b2f780aba4"
branch_labels = None
depends_on = None


def generate_uuid() -> str:
    return str(uuid4())


def upgrade():
    op.create_table(
        "registered_hours_worked",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("company", sa.String(), nullable=False),
        sa.Column("worker", sa.String(), nullable=False),
        sa.Column("transaction", sa.String(), nullable=False),
        sa.Column("amount", sa.Numeric(), nullable=False),
        sa.Column("registered_on", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["company"],
            ["company.id"],
        ),
        sa.ForeignKeyConstraint(
            ["worker"],
            ["member.id"],
        ),
        sa.ForeignKeyConstraint(
            ["transaction"],
            ["transaction.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    Base = orm.declarative_base()

    class RegisteredHoursWorked(Base):
        __tablename__ = "registered_hours_worked"
        id = sa.Column(sa.String, primary_key=True, default=generate_uuid)
        company = sa.Column(sa.String, sa.ForeignKey("company.id"), nullable=False)
        worker = sa.Column(sa.String, sa.ForeignKey("member.id"), nullable=False)
        amount = sa.Column(sa.Numeric(), nullable=False)
        transaction = sa.Column(sa.String, sa.ForeignKey("transaction.id"), nullable=True)
        registered_on = sa.Column(sa.DateTime, nullable=False)

    class Company(Base):
        __tablename__ = "company"
        id = sa.Column(sa.String, primary_key=True, default=generate_uuid)
        a_account = sa.Column(sa.ForeignKey("account.id"), nullable=False)

    class Transaction(Base):
        __tablename__ = "transaction"
        id = sa.Column(sa.String, primary_key=True, default=generate_uuid)
        sending_account = sa.Column(
            sa.String, sa.ForeignKey("account.id"), nullable=False
        )
        receiving_account = sa.Column(
            sa.String, sa.ForeignKey("account.id"), nullable=False
        )
        amount_sent = sa.Column(sa.Numeric(), nullable=False)
        date = sa.Column(sa.DateTime, nullable=False)

    class Account(Base):
        __tablename__ = "account"
        id = sa.Column(sa.String, primary_key=True, default=generate_uuid)

    class Member(Base):
        __tablename__ = "member"
        id = sa.Column(sa.String, primary_key=True, default=generate_uuid)
        account = sa.Column(sa.ForeignKey("account.id"), nullable=False)

    bind = op.get_bind()
    with orm.Session(bind=bind) as session:
        sending_account = orm.aliased(Account)
        receiving_account = orm.aliased(Account)
        transactions = (
            session.query(Transaction)
            .join(
                sending_account,
                sending_account.id == Transaction.sending_account,
            )
            .join(
                receiving_account,
                receiving_account.id == Transaction.receiving_account,
            )
            .join(
                Member,
                Member.account == receiving_account.id,
            )
            .join(
                Company,
                Company.a_account == sending_account.id,
            )
            .with_entities(Transaction, Company, Member)
        )
        for transaction, company, member in transactions:
            session.add(
                RegisteredHoursWorked(
                    company=company.id,
                    worker=member.id,
                    amount=transaction.amount_sent,
                    transaction=transaction.id,
                    registered_on=transaction.date,
                )
            )
        session.flush()


def downgrade():
    op.drop_table("registered_hours_worked")
