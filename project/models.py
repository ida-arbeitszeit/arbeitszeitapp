"""
Definition of database tables.
"""

from enum import Enum
from flask_login import UserMixin
from sqlalchemy.orm import backref
from project.extensions import db


class SocialAccounting(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)


# Association table Company - Member
jobs = db.Table(
    "jobs",
    db.Column("member_id", db.Integer, db.ForeignKey("member.id")),
    db.Column("company_id", db.Integer, db.ForeignKey("company.id")),
)


class Member(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
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
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)

    plans = db.relationship("Plan", lazy="dynamic", backref="company")
    accounts = db.relationship("Account", lazy="dynamic", backref="company")

    def __repr__(self):
        return "<Company(email='%s', name='%s')>" % (
            self.email,
            self.name,
        )


class Plan(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_creation_date = db.Column(db.DateTime, nullable=False)
    planner = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    costs_p = db.Column(db.Numeric(), nullable=False)
    costs_r = db.Column(db.Numeric(), nullable=False)
    costs_a = db.Column(db.Numeric(), nullable=False)
    prd_name = db.Column(db.String(100), nullable=False)
    prd_unit = db.Column(db.String(100), nullable=False)
    prd_amount = db.Column(db.Numeric(), nullable=False)
    description = db.Column(db.String(2000), nullable=False)
    timeframe = db.Column(db.Numeric(), nullable=False)
    social_accounting = db.Column(
        db.Integer, db.ForeignKey("social_accounting.id"), nullable=False
    )
    approved = db.Column(db.Boolean, nullable=False, default=False)
    approval_date = db.Column(db.DateTime, nullable=True, default=None)
    approval_reason = db.Column(db.String(1000), nullable=True, default=None)

    offers = db.relationship("Offer", lazy="dynamic", backref="plan")


class AccountTypes(Enum):
    p = "p"
    r = "r"
    a = "a"
    prd = "prd"
    member = "member"
    accounting = "accounting"


class Account(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    account_owner_social_accounting = db.Column(
        db.Integer, db.ForeignKey("social_accounting.id"), nullable=True
    )
    account_owner_company = db.Column(
        db.Integer, db.ForeignKey("company.id"), nullable=True
    )
    account_owner_member = db.Column(
        db.Integer, db.ForeignKey("member.id"), nullable=True
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
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    account_from = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    account_to = db.Column(db.Integer, db.ForeignKey("account.id"), nullable=False)
    amount = db.Column(db.Numeric(), nullable=False)
    purpose = db.Column(db.String(1000), nullable=True)  # Verwendungszweck


class Offer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("plan.id"), nullable=False)
    cr_date = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    amount_available = db.Column(db.Numeric(), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)

    purchases = db.relationship("Kaeufe", lazy="dynamic", backref="offer")


class PurposesOfPurchases(Enum):
    means_of_prod = "means_of_prod"
    raw_materials = "raw_materials"
    consumption = "consumption"


class Kaeufe(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kauf_date = db.Column(db.DateTime, nullable=False)
    angebot = db.Column(db.Integer, db.ForeignKey("offer.id"), nullable=False)
    type_member = db.Column(db.Boolean, nullable=False)
    company = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=True)
    member = db.Column(db.Integer, db.ForeignKey("member.id"), nullable=True)
    kaufpreis = db.Column(db.Numeric(), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    purpose = db.Column(db.Enum(PurposesOfPurchases), nullable=False)


class Withdrawal(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_member = db.Column(db.Boolean, nullable=False)
    member = db.Column(db.Integer, db.ForeignKey("member.id"), nullable=False)
    betrag = db.Column(db.Numeric(), nullable=False)
    code = db.Column(db.String(100), nullable=False)
    entwertet = db.Column(db.Boolean, nullable=False, default=False)
