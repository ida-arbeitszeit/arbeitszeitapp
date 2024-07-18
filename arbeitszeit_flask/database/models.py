"""
Definition of database tables.
"""

import uuid
from enum import Enum

from flask_login import UserMixin

from arbeitszeit_flask.extensions import db


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    password = db.Column(db.String(300), nullable=False)
    email_address = db.Column(
        db.ForeignKey("email.address"), nullable=False, unique=True
    )

    def __str__(self) -> str:
        return f"User {self.email_address} ({self.id})"


class Email(db.Model):
    address = db.Column(db.String, primary_key=True, nullable=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)


class SocialAccounting(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    account = db.Column(db.ForeignKey("account.id"), nullable=False)


# Association table Company - Member
jobs = db.Table(
    "jobs",
    db.Column("member_id", db.String, db.ForeignKey("member.id")),
    db.Column("company_id", db.String, db.ForeignKey("company.id")),
)


class Member(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False, unique=True)
    name = db.Column(db.String(1000), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    account = db.Column(db.ForeignKey("account.id"), nullable=False)

    workplaces = db.relationship(
        "Company",
        secondary=jobs,
        lazy="dynamic",
        backref=db.backref("workers", lazy="dynamic"),
    )


class Company(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False, unique=True)
    name = db.Column(db.String(1000), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    p_account = db.Column(db.ForeignKey("account.id"), nullable=False)
    r_account = db.Column(db.ForeignKey("account.id"), nullable=False)
    a_account = db.Column(db.ForeignKey("account.id"), nullable=False)
    prd_account = db.Column(db.ForeignKey("account.id"), nullable=False)

    def __repr__(self):
        return "<Company(name='%s')>" % (self.name,)


class Accountant(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False, unique=True)
    name = db.Column(db.String(1000), nullable=False)


class PlanDraft(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    plan_creation_date = db.Column(db.DateTime, nullable=False)
    planner = db.Column(db.String, db.ForeignKey("company.id"), nullable=False)
    costs_p = db.Column(db.Numeric(), nullable=False)
    costs_r = db.Column(db.Numeric(), nullable=False)
    costs_a = db.Column(db.Numeric(), nullable=False)
    prd_name = db.Column(db.String(100), nullable=False)
    prd_unit = db.Column(db.String(100), nullable=False)
    prd_amount = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(5000), nullable=False)
    timeframe = db.Column(db.Numeric(), nullable=False)
    is_public_service = db.Column(db.Boolean, nullable=False, default=False)


class Plan(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    plan_creation_date = db.Column(db.DateTime, nullable=False)
    planner = db.Column(db.String, db.ForeignKey("company.id"), nullable=False)
    costs_p = db.Column(db.Numeric(), nullable=False)
    costs_r = db.Column(db.Numeric(), nullable=False)
    costs_a = db.Column(db.Numeric(), nullable=False)
    prd_name = db.Column(db.String(100), nullable=False)
    prd_unit = db.Column(db.String(100), nullable=False)
    prd_amount = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(5000), nullable=False)
    timeframe = db.Column(db.Numeric(), nullable=False)
    is_public_service = db.Column(db.Boolean, nullable=False, default=False)
    activation_date = db.Column(db.DateTime, nullable=True)
    requested_cooperation = db.Column(
        db.String, db.ForeignKey("cooperation.id"), nullable=True
    )
    hidden_by_user = db.Column(db.Boolean, nullable=False, default=False)

    review = db.relationship("PlanReview", uselist=False, back_populates="plan")


class PlanCooperation(db.Model):
    plan = db.Column(
        db.String, db.ForeignKey("plan.id"), nullable=False, primary_key=True
    )
    cooperation = db.Column(db.String, db.ForeignKey("cooperation.id"), nullable=False)


class PlanReview(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    approval_date = db.Column(db.DateTime, nullable=True, default=None)
    plan_id = db.Column(
        db.String, db.ForeignKey("plan.id", ondelete="CASCADE"), nullable=False
    )

    plan = db.relationship("Plan", back_populates="review")

    def __repr__(self) -> str:
        return f"PlanReview(id={self.id!r}, plan_id={self.plan_id!r}, approval_date={self.approval_date!r})"


class AccountTypes(Enum):
    p = "p"
    r = "r"
    a = "a"
    prd = "prd"
    member = "member"
    accounting = "accounting"


class Account(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)

    transactions_sent = db.relationship(
        "Transaction",
        foreign_keys="Transaction.sending_account",
        lazy="dynamic",
        backref=db.backref("account_from"),
    )
    transactions_received = db.relationship(
        "Transaction",
        foreign_keys="Transaction.receiving_account",
        lazy="dynamic",
        backref=db.backref("account_to"),
    )


class Transaction(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    date = db.Column(db.DateTime, nullable=False)
    sending_account = db.Column(db.String, db.ForeignKey("account.id"), nullable=False)
    receiving_account = db.Column(
        db.String, db.ForeignKey("account.id"), nullable=False
    )
    amount_sent = db.Column(db.Numeric(), nullable=False)
    amount_received = db.Column(db.Numeric(), nullable=False)
    purpose = db.Column(db.String(1000), nullable=True)  # Verwendungszweck

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


class PrivateConsumption(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    plan_id = db.Column(db.String, db.ForeignKey("plan.id"), nullable=False)
    transaction_id = db.Column(
        db.String, db.ForeignKey("transaction.id"), nullable=True
    )
    amount = db.Column(db.Integer, nullable=False)


class ProductiveConsumption(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    plan_id = db.Column(db.String, db.ForeignKey("plan.id"), nullable=False)
    transaction_id = db.Column(
        db.String, db.ForeignKey("transaction.id"), nullable=True
    )
    amount = db.Column(db.Integer, nullable=False)


class RegisteredHoursWorked(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    company = db.Column(db.String, db.ForeignKey("company.id"), nullable=False)
    worker = db.Column(db.String, db.ForeignKey("member.id"), nullable=False)
    amount = db.Column(db.Numeric(), nullable=False)
    transaction = db.Column(db.String, db.ForeignKey("transaction.id"), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)


class CompanyWorkInvite(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    company = db.Column(db.String, db.ForeignKey("company.id"), nullable=False)
    member = db.Column(db.String, db.ForeignKey("member.id"), nullable=False)


class Cooperation(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    creation_date = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    definition = db.Column(db.String(5000), nullable=False)


class CoordinationTenure(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    company = db.Column(db.String, db.ForeignKey("company.id"), nullable=False)
    cooperation = db.Column(db.String, db.ForeignKey("cooperation.id"), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)


class CoordinationTransferRequest(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    requesting_coordination_tenure = db.Column(
        db.String, db.ForeignKey("coordination_tenure.id"), nullable=False
    )
    candidate = db.Column(db.String, db.ForeignKey("company.id"), nullable=False)
    request_date = db.Column(db.DateTime, nullable=False)


class PasswordResetRequest(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    email_address = db.Column(
        db.String, db.ForeignKey("email.address"), nullable=False, unique=False
    )
    reset_token = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
