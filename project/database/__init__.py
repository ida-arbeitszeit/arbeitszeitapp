from __future__ import annotations

from injector import inject

from arbeitszeit import entities
from project.extensions import db
from project.models import Company, Member

from .repositories import (
    AccountingRepository,
    AccountOwnerRepository,
    AccountRepository,
    CompanyRepository,
    CompanyWorkerRepository,
    MemberRepository,
    PlanRepository,
    ProductOfferRepository,
    PurchaseRepository,
    TransactionRepository,
)

__all__ = [
    "AccountOwnerRepository",
    "AccountRepository",
    "AccountingRepository",
    "CompanyRepository",
    "CompanyWorkerRepository",
    "MemberRepository",
    "PlanRepository",
    "ProductOfferRepository",
    "PurchaseRepository",
    "TransactionRepository",
    "commit_changes",
    "get_company_by_mail",
]


@inject
def get_social_accounting(
    accounting_repo: AccountingRepository,
) -> entities.SocialAccounting:
    return accounting_repo.get_or_create_social_accounting()


def commit_changes():
    db.session.commit()


def get_user_by_mail(email) -> Member:
    """returns first user in User, filtered by email."""
    member = Member.query.filter_by(email=email).first()
    return member


def get_company_by_mail(email) -> Company:
    """returns first company in Company, filtered by mail."""
    company = Company.query.filter_by(email=email).first()
    return company
