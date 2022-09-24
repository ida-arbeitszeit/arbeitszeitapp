"""
Definition of database tables.
"""

import uuid
from enum import Enum

from flask_login import UserMixin

from arbeitszeit import entities
from arbeitszeit_flask.extensions import db


def generate_uuid() -> str:
    return str(uuid.uuid4())


class User(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


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
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)

    account = db.relationship("Account", uselist=False, lazy=True, backref="member")
    purchases = db.relationship("Purchase", lazy="dynamic")
    user = db.relationship("User", lazy=True, uselist=False, backref="member")

    workplaces = db.relationship(
        "Company",
        secondary=jobs,
        lazy="dynamic",
        backref=db.backref("workers", lazy="dynamic"),
    )


class Company(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", lazy=True, uselist=False, backref="company")
    plans = db.relationship("Plan", lazy="dynamic", backref="company")
    accounts = db.relationship("Account", lazy="dynamic", backref="company")
    purchases = db.relationship("Purchase", lazy="dynamic")
    drafts = db.relationship("PlanDraft", lazy="dynamic")

    def __repr__(self):
        return "<Company(name='%s')>" % (self.name,)


class Accountant(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    user_id = db.Column(db.ForeignKey("user.id"), nullable=False)
    name = db.Column(db.String(1000), nullable=False)

    user = db.relationship("User", lazy=True, uselist=False, backref="accountant")


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
    approval_date = db.Column(db.DateTime, nullable=True, default=None)
    approval_reason = db.Column(db.String(1000), nullable=True, default=None)
    is_active = db.Column(db.Boolean, nullable=False, default=False)
    activation_date = db.Column(db.DateTime, nullable=True)
    expired = db.Column(db.Boolean, nullable=False, default=False)
    expiration_date = db.Column(db.DateTime, nullable=True)
    active_days = db.Column(db.Integer, nullable=True)
    payout_count = db.Column(db.Integer, nullable=False, default=0)
    is_available = db.Column(db.Boolean, nullable=False, default=True)
    requested_cooperation = db.Column(
        db.String, db.ForeignKey("cooperation.id"), nullable=True
    )
    cooperation = db.Column(db.String, db.ForeignKey("cooperation.id"), nullable=True)
    hidden_by_user = db.Column(db.Boolean, nullable=False, default=False)


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
    amount_sent = db.Column(db.Numeric(), nullable=False)
    amount_received = db.Column(db.Numeric(), nullable=False)
    purpose = db.Column(db.String(1000), nullable=True)  # Verwendungszweck


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


class Cooperation(db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    creation_date = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    definition = db.Column(db.String(5000), nullable=False)
    coordinator = db.Column(db.String, db.ForeignKey("company.id"), nullable=False)

    plans = db.relationship(
        "Plan", foreign_keys="Plan.cooperation", lazy="dynamic", backref="coop"
    )


class PayoutFactor(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    timestamp = db.Column(db.DateTime, nullable=False)
    payout_factor = db.Column(db.Numeric(), nullable=False)
