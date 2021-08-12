"""
Definition of database tables.
"""

import uuid
from enum import Enum

from flask_login import UserMixin

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
    purchases = db.relationship("Kaeufe", lazy="dynamic")

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
    purchases = db.relationship("Kaeufe", lazy="dynamic")

    def __repr__(self):
        return "<Company(email='%s', name='%s')>" % (
            self.email,
            self.name,
        )


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
    social_accounting = db.Column(
        db.String, db.ForeignKey("social_accounting.id"), nullable=False
    )
    approved = db.Column(db.Boolean, nullable=False, default=False)
    approval_date = db.Column(db.DateTime, nullable=True, default=None)
    approval_reason = db.Column(db.String(1000), nullable=True, default=None)
    expired = db.Column(db.Boolean, nullable=False, default=False)
    renewed = db.Column(db.Boolean, nullable=False, default=False)

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
    balance = db.Column(db.Numeric(), default=0)

    transactions_sent = db.relationship(
        "Transaction",
        foreign_keys="Transaction.account_from",
        lazy="dynamic",
        backref="sending_account",
    )
    transactions_received = db.relationship(
        "Transaction",
        foreign_keys="Transaction.account_to",
        lazy="dynamic",
        backref="receiving_account",
    )


class Transaction(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    date = db.Column(db.DateTime, nullable=False)
    account_from = db.Column(db.String, db.ForeignKey("account.id"), nullable=False)
    account_to = db.Column(db.String, db.ForeignKey("account.id"), nullable=False)
    amount = db.Column(db.Numeric(), nullable=False)
    purpose = db.Column(db.String(1000), nullable=True)  # Verwendungszweck


class Offer(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    plan_id = db.Column(db.String, db.ForeignKey("plan.id"), nullable=False)
    cr_date = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    description = db.Column(db.String(5000), nullable=False)
    amount_available = db.Column(db.Numeric(), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)

    purchases = db.relationship("Kaeufe", lazy="dynamic", backref="offer")


class PurposesOfPurchases(Enum):
    means_of_prod = "means_of_prod"
    raw_materials = "raw_materials"
    consumption = "consumption"


class Kaeufe(UserMixin, db.Model):
    id = db.Column(db.String, primary_key=True, default=generate_uuid)
    kauf_date = db.Column(db.DateTime, nullable=False)
    angebot = db.Column(db.String, db.ForeignKey("offer.id"), nullable=False)
    type_member = db.Column(db.Boolean, nullable=False)
    company = db.Column(db.String, db.ForeignKey("company.id"), nullable=True)
    member = db.Column(db.String, db.ForeignKey("member.id"), nullable=True)
    kaufpreis = db.Column(db.Numeric(), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    purpose = db.Column(db.Enum(PurposesOfPurchases), nullable=False)
