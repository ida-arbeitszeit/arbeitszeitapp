"""
Definition of database tables.
"""

import enum
from flask_login import UserMixin
from sqlalchemy.orm import backref
from project.extensions import db


class SocialAccounting(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    transactions = db.relationship(
        "TransactionsAccountingToCompany",
        lazy="dynamic",
    )


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
    guthaben = db.Column(db.Numeric(), default=0, nullable=False)

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
    guthaben = db.Column(db.Numeric(), default=0)
    balance_p = db.Column(db.Numeric(), default=0)
    balance_r = db.Column(db.Numeric(), default=0)
    balance_a = db.Column(db.Numeric(), default=0)
    balance_prd = db.Column(db.Numeric(), default=0)

    plans = db.relationship("Plan", lazy="dynamic", backref="company")

    def __repr__(self):
        return "<Company(email='%s', name='%s', guthaben='%s')>" % (
            self.email,
            self.name,
            self.guthaben,
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


class CompanyAccountTypes(enum.Enum):
    p = "p"
    r = "r"
    a = "a"
    prd = "prd"


class TransactionsAccountingToCompany(UserMixin, db.Model):
    """Transactions made by social accounting institutions to companies."""

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    account_owner = db.Column(
        db.Integer, db.ForeignKey("social_accounting.id"), nullable=False
    )
    receiver_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    receiver_account_type = db.Column(db.Enum(CompanyAccountTypes), nullable=False)
    amount = db.Column(db.Numeric(), nullable=False)
    purpose = db.Column(db.String(1000), nullable=True)


class TransactionsCompanyToMember(UserMixin, db.Model):
    """Transactions made by companies to members. E.g. salaries."""

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    account_owner = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("member.id"), nullable=False)
    amount = db.Column(db.Numeric(), nullable=False)
    purpose = db.Column(db.String(1000), nullable=True)


class TransactionsCompanyToCompany(UserMixin, db.Model):
    """Transactions made by companies to companies. E.g. purchase of means of production."""

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    account_owner = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    owner_account_type = db.Column(db.Enum(CompanyAccountTypes), nullable=False)
    receiver_account_type = db.Column(db.Enum(CompanyAccountTypes), nullable=False)
    amount = db.Column(db.Numeric(), nullable=False)
    purpose = db.Column(db.String(1000), nullable=True)


class TransactionsMemberToCompany(UserMixin, db.Model):
    """Transactions made by members to companies. E.g. purchases."""

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    account_owner = db.Column(db.Integer, db.ForeignKey("member.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    amount = db.Column(db.Numeric(), nullable=False)
    purpose = db.Column(db.String(1000), nullable=True)


class Offer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey("plan.id"), nullable=False)
    cr_date = db.Column(db.DateTime, nullable=False)
    name = db.Column(db.String(1000), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    amount_available = db.Column(db.Numeric(), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)

    purchases = db.relationship("Kaeufe", lazy="dynamic", backref="offer")


class Kaeufe(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kauf_date = db.Column(db.DateTime, nullable=False)
    angebot = db.Column(db.Integer, db.ForeignKey("offer.id"), nullable=False)
    type_member = db.Column(db.Boolean, nullable=False)
    company = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=True)
    member = db.Column(db.Integer, db.ForeignKey("member.id"), nullable=True)
    kaufpreis = db.Column(db.Numeric(), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    purpose = db.Column(db.String(100), nullable=False)


class Withdrawal(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type_member = db.Column(db.Boolean, nullable=False)
    member = db.Column(db.Integer, db.ForeignKey("member.id"), nullable=False)
    betrag = db.Column(db.Numeric(), nullable=False)
    code = db.Column(db.String(100), nullable=False)
    entwertet = db.Column(db.Boolean, nullable=False, default=False)
