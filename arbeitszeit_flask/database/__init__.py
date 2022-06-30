from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from injector import inject

from arbeitszeit import entities
from arbeitszeit_flask.extensions import db
from arbeitszeit_flask.models import Company, Member

from .repositories import (
    AccountingRepository,
    AccountOwnerRepository,
    AccountRepository,
    CompanyRepository,
    CompanyWorkerRepository,
    MemberRepository,
    PlanRepository,
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


def commit_changes(function: Callable) -> Callable:
    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = function(*args, **kwargs)
        db.session.commit()
        return result

    return wrapper


def get_member_by_mail(email) -> Member:
    """returns first user in User, filtered by email."""
    member = Member.query.filter_by(email=email).first()
    return member


def get_company_by_mail(email) -> Company:
    """returns first company in Company, filtered by mail."""
    company = Company.query.filter_by(email=email).first()
    return company
