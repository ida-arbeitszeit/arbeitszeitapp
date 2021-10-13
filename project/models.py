"""
Definition of database tables.
"""

import uuid
from enum import Enum

from flask_login import UserMixin

from arbeitszeit import entities
from project.extensions import db


def generate_uuid() -> str:
    return str(uuid.uuid4())


class SocialAccounting(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)

    account = db.relationship(
        "Account", uselist=False, lazy=True, backref="social_accounting"
    )


# Association table Company - Member
jobs = db.Table(
    "jobs",
    db.Column("member_id", db.String, db.ForeignKey("member.id")),
    db.Column("company_id", db.String, db.ForeignKey("company.id")),
)


class Member(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)

    account = db.relationship("Account", uselist=False, lazy=True, backref="member")
    purchases = db.relationship("Purchase", lazy="dynamic")

    workplaces = db.relationship(
        "Company",
        secondary=jobs,
        lazy="dynamic",
        backref=db.backref("workers", lazy="dynamic"),
    )


class Company(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)

    plans = db.relationship("Plan", lazy="dynamic", backref="company")
    accounts = db.relationship("Account", lazy="dynamic", backref="company")
    purchases = db.relationship("Purchase", lazy="dynamic")

    def __repr__(self):
        return "<Company(email='%s', name='%s')>" % (
            self.email,
            self.name,
        )


class PlanDraft(UserMixin, db.Model):
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


class Plan(UserMixin, db.Model):
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
    approved = db.Column(db.Boolean, nullable=False, default=False)
    approval_date = db.Column(db.DateTime, nullable=True, default=None)
    approval_reason = db.Column(db.String(1000), nullable=True, default=None)
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    activation_date = db.Column(db.DateTime, nullable=True)
    expired = db.Column(db.Boolean, nullable=False, default=False)
    renewed = db.Column(db.Boolean, nullable=False, default=False)
    last_certificate_payout = db.Column(db.DateTime, nullable=True)
    expiration_date = db.Column(db.DateTime, nullable=True)
    expiration_relative = db.Column(db.Integer, nullable=True)

    offers = db.relationship("Offer", lazy="dynamic", backref="plan")


class AccountTypes(Enum):
    p = "p"
    r = "r"
    a = "a"
    prd = "prd"
    member = "member"
    accounting = "accounting"


class Account(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    account_owner_social_accounting = db.Column(
        db.String, db.ForeignKey("social_accounting.id"), nullable=True
    )
    account_owner_company = db.Column(
        db.String, db.ForeignKey("company.id"), nullable=True
    )
    account_owner_member = db.Column(
        db.String, db.ForeignKey("member.id"), nullable=True
    )
    account_type = db.Column(db.Enum(AccountTypes), nullable=False)
    transactions_sent = db.relationship(
        "Transaction",
        foreign_keys="Transaction.sending_account",
        lazy="dynamic",
        backref="account_from",
    )
    transactions_received = db.relationship(
        "Transaction",
        foreign_keys="Transaction.receiving_account",
        lazy="dynamic",
        backref="account_to",
    )


class Transaction(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    date = db.Column(db.DateTime, nullable=False)
    sending_account = db.Column(db.String, db.ForeignKey("account.id"), nullable=False)
    receiving_account = db.Column(
        db.String, db.ForeignKey("account.id"), nullable=False
    )
    amount = db.Column(db.Numeric(), nullable=False)
    purpose = db.Column(db.String(1000), nullable=True)  # Verwendungszweck


class Offer(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    plan_id = db.Column(db.String, db.ForeignKey("plan.id"), nullable=False)
    cr_date = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    description = db.Column(db.String(5000), nullable=False)


class Purchase(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    purchase_date = db.Column(db.DateTime, nullable=False)
    plan_id = db.Column(db.String, db.ForeignKey("plan.id"), nullable=False)
    type_member = db.Column(db.Boolean, nullable=False)
    company = db.Column(db.String, db.ForeignKey("company.id"), nullable=True)
    member = db.Column(db.String, db.ForeignKey("member.id"), nullable=True)
    price_per_unit = db.Column(db.Numeric(), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    purpose = db.Column(db.Enum(entities.PurposesOfPurchases), nullable=False)


class CompanyWorkInvite(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    company = db.Column(db.String, db.ForeignKey("company.id"), nullable=False)
    member = db.Column(db.String, db.ForeignKey("member.id"), nullable=False)
