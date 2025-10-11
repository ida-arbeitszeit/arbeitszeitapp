from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from arbeitszeit import records
from arbeitszeit_db.db import Database

from .repositories import AccountingRepository

__all__ = [
    "AccountingRepository",
    "commit_changes",
]


def get_social_accounting(
    accounting_repo: AccountingRepository,
) -> records.SocialAccounting:
    return accounting_repo.get_or_create_social_accounting()


def commit_changes(function: Callable) -> Callable:
    @wraps(function)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        result = function(*args, **kwargs)
        Database().session.commit()
        return result

    return wrapper
