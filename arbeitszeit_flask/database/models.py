"""
Definition of database tables.
"""

import uuid
from datetime import datetime
from decimal import Decimal

from flask_login import UserMixin
from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from arbeitszeit_flask.database.db import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "user"

    id: Mapped[str] = mapped_column(primary_key=True, default=generate_uuid)
    password: Mapped[str] = mapped_column(String(300))
    email_address: Mapped[str] = mapped_column(ForeignKey("email.address"), unique=True)

    def __str__(self) -> str:
        return f"User {self.email_address} ({self.id})"


class Email(Base):
    __tablename__ = "email"

    address: Mapped[str] = mapped_column(primary_key=True)
    confirmed_on: Mapped[datetime | None]


class SocialAccounting(Base):
    __tablename__ = "social_accounting"

    id: Mapped[str] = mapped_column(primary_key=True, default=generate_uuid)
    account: Mapped[str] = mapped_column(ForeignKey("account.id"))
    account_psf: Mapped[str] = mapped_column(ForeignKey("account.id"))


# Association table Company - Member
jobs_table = Table(
    "jobs",
    Base.metadata,
    Column("member_id", String, ForeignKey("member.id"), primary_key=True),
    Column("company_id", String, ForeignKey("company.id"), primary_key=True),
)


class Member(UserMixin, Base):
    __tablename__ = "member"

    id: Mapped[str] = mapped_column(primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.id"), unique=True)
    name: Mapped[str] = mapped_column(String(1000))
    registered_on: Mapped[datetime]
    account: Mapped[str] = mapped_column(ForeignKey("account.id"))

    workplaces = relationship(
        "Company",
        secondary=jobs_table,
        back_populates="workers",
    )


class Company(UserMixin, Base):
    __tablename__ = "company"

    id: Mapped[str] = mapped_column(primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.id"), unique=True)
    name: Mapped[str] = mapped_column(String(1000))
    registered_on: Mapped[datetime]
    p_account: Mapped[str] = mapped_column(ForeignKey("account.id"))
    r_account: Mapped[str] = mapped_column(ForeignKey("account.id"))
    a_account: Mapped[str] = mapped_column(ForeignKey("account.id"))
    prd_account: Mapped[str] = mapped_column(ForeignKey("account.id"))

    def __repr__(self):
        return "<Company(name='%s')>" % (self.name,)

    workers = relationship(
        "Member",
        secondary=jobs_table,
        back_populates="workplaces",
    )


class Accountant(UserMixin, Base):
    __tablename__ = "accountant"

    id: Mapped[str] = mapped_column(primary_key=True, default=generate_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("user.id"), unique=True)
    name: Mapped[str] = mapped_column(String(1000))


class PlanDraft(Base):
    __tablename__ = "plan_draft"

    id: Mapped[str] = mapped_column(primary_key=True, default=generate_uuid)
    plan_creation_date: Mapped[datetime]
    planner: Mapped[str] = mapped_column(ForeignKey("company.id"))
    costs_p: Mapped[Decimal]
    costs_r: Mapped[Decimal]
    costs_a: Mapped[Decimal]
    prd_name: Mapped[str] = mapped_column(String(100))
    prd_unit: Mapped[str] = mapped_column(String(100))
    prd_amount: Mapped[int]
    description: Mapped[str] = mapped_column(String(5000))
    timeframe: Mapped[Decimal]
    is_public_service: Mapped[bool] = mapped_column(default=False)


class Plan(Base):
    __tablename__ = "plan"

    id: Mapped[str] = mapped_column(primary_key=True, default=generate_uuid)
    plan_creation_date: Mapped[datetime]
    planner: Mapped[str] = mapped_column(ForeignKey("company.id"))
    costs_p: Mapped[Decimal]
    costs_r: Mapped[Decimal]
    costs_a: Mapped[Decimal]
    prd_name: Mapped[str] = mapped_column(String(100))
    prd_unit: Mapped[str] = mapped_column(String(100))
    prd_amount: Mapped[int]
    description: Mapped[str] = mapped_column(String(5000))
    timeframe: Mapped[Decimal]
    is_public_service: Mapped[bool] = mapped_column(default=False)
    requested_cooperation: Mapped[str | None] = mapped_column(
        ForeignKey("cooperation.id")
    )
    hidden_by_user: Mapped[bool] = mapped_column(default=False)

    review: Mapped["PlanReview  | None"] = relationship(
        "PlanReview", uselist=False, back_populates="plan"
    )


class PlanCooperation(Base):
    __tablename__ = "plan_cooperation"

    plan: Mapped[str] = mapped_column(ForeignKey("plan.id"), primary_key=True)
    cooperation: Mapped[str] = mapped_column(ForeignKey("cooperation.id"))


class PlanReview(Base):
    __tablename__ = "plan_review"

    id: Mapped[str] = mapped_column(primary_key=True, default=generate_uuid)
    approval_date: Mapped[datetime | None]
    rejection_date: Mapped[datetime | None]
    plan_id: Mapped[str] = mapped_column(ForeignKey("plan.id", ondelete="CASCADE"))

    plan: Mapped["Plan"] = relationship("Plan", back_populates="review")

    def __repr__(self) -> str:
        return f"PlanReview(id={self.id!r}, plan_id={self.plan_id!r}, approval_date={self.approval_date!r}, rejection_date={self.rejection_date!r})"


class Account(Base):
    __tablename__ = "account"

    id: Mapped[str] = mapped_column(primary_key=True, default=generate_uuid)


class Transaction(Base):
    __tablename__ = "transaction"

    id: Mapped[str] = mapped_column(primary_key=True, default=generate_uuid)
    date: Mapped[datetime]
    sending_account: Mapped[str] = mapped_column(ForeignKey("account.id"))
    receiving_account: Mapped[str] = mapped_column(ForeignKey("account.id"))
    amount_sent: Mapped[Decimal]
    amount_received: Mapped[Decimal]
    purpose: Mapped[str] = mapped_column(String(1000), default="")  # Verwendungszweck

    def __repr__(self) -> str:
        fields = ", ".join(
            [
                f"id={self.id!r}",
                f"date={self.date!r}",
                f"sending_account={self.sending_account!r}",
                f"receiving_account={self.receiving_account!r}",
                f"amount_sent={self.amount_sent!r}",
                f"amount_received={self.amount_received!r}",
                f"purpose={self.purpose!r}",
            ]
        )
        return f"Transaction({fields})"


class Transfer(Base):
    __tablename__ = "transfer"

    id: Mapped[str] = mapped_column(primary_key=True, default=generate_uuid)
    date: Mapped[datetime] = mapped_column(index=True)
    debit_account: Mapped[str] = mapped_column(ForeignKey("account.id"), index=True)
    credit_account: Mapped[str] = mapped_column(ForeignKey("account.id"), index=True)
    value: Mapped[Decimal]

    def __repr__(self) -> str:
        fields = ", ".join(
            [
                f"id={self.id!r}",
                f"date={self.date!r}",
                f"debit_account={self.debit_account!r}",
                f"credit_account={self.credit_account!r}",
                f"value={self.value!r}",
            ]
        )
        return f"Transfer({fields})"


class PrivateConsumption(Base):
    __tablename__ = "private_consumption"

    id: Mapped[str] = mapped_column(primary_key=True, default=generate_uuid)
    plan_id: Mapped[str] = mapped_column(ForeignKey("plan.id"))
    transaction_id: Mapped[str | None] = mapped_column(ForeignKey("transaction.id"))
    amount: Mapped[int]


class ProductiveConsumption(Base):
    __tablename__ = "productive_consumption"

    id: Mapped[str] = mapped_column(primary_key=True, default=generate_uuid)
    plan_id: Mapped[str] = mapped_column(ForeignKey("plan.id"))
    transaction_id: Mapped[str | None] = mapped_column(ForeignKey("transaction.id"))
    amount: Mapped[int]


class RegisteredHoursWorked(Base):
    __tablename__ = "registered_hours_worked"

    id: Mapped[str] = mapped_column(primary_key=True, default=generate_uuid)
    company: Mapped[str] = mapped_column(ForeignKey("company.id"))
    worker: Mapped[str] = mapped_column(ForeignKey("member.id"))
    transfer_of_work_certificates: Mapped[str] = mapped_column(
        ForeignKey("transfer.id")
    )
    transfer_of_taxes: Mapped[str] = mapped_column(ForeignKey("transfer.id"))
    registered_on: Mapped[datetime]


class CompanyWorkInvite(Base):
    __tablename__ = "company_work_invite"

    id: Mapped[str] = mapped_column(primary_key=True, default=generate_uuid)
    company: Mapped[str] = mapped_column(ForeignKey("company.id"))
    member: Mapped[str] = mapped_column(ForeignKey("member.id"))


class Cooperation(Base):
    __tablename__ = "cooperation"

    id: Mapped[str] = mapped_column(primary_key=True, default=generate_uuid)
    creation_date: Mapped[datetime]
    name: Mapped[str] = mapped_column(String(100))
    definition: Mapped[str] = mapped_column(String(5000))
    account: Mapped[str] = mapped_column(ForeignKey("account.id"))


class CoordinationTenure(Base):
    __tablename__ = "coordination_tenure"

    id: Mapped[str] = mapped_column(primary_key=True, default=generate_uuid)
    company: Mapped[str] = mapped_column(ForeignKey("company.id"))
    cooperation: Mapped[str] = mapped_column(ForeignKey("cooperation.id"))
    start_date: Mapped[datetime]


class CoordinationTransferRequest(Base):
    __tablename__ = "coordination_transfer_request"

    id: Mapped[str] = mapped_column(primary_key=True, default=generate_uuid)
    requesting_coordination_tenure: Mapped[str] = mapped_column(
        ForeignKey("coordination_tenure.id")
    )
    candidate: Mapped[str] = mapped_column(ForeignKey("company.id"))
    request_date: Mapped[datetime]


class PasswordResetRequest(Base):
    __tablename__ = "password_reset_request"

    id: Mapped[str] = mapped_column(primary_key=True, default=generate_uuid)
    email_address: Mapped[str] = mapped_column(
        ForeignKey("email.address"), unique=False
    )
    reset_token: Mapped[str] = mapped_column(String(300))
    created_at: Mapped[datetime]
