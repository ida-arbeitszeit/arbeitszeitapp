from dataclasses import dataclass
from typing import Optional
from urllib.parse import urljoin, urlparse
from uuid import UUID

from flask import request, session
from flask_login import current_user, login_user, logout_user

from arbeitszeit_flask.database import models
from arbeitszeit_flask.database.db import Database
from arbeitszeit_web.session import UserRole


def is_safe_url(target: str, host_url: str) -> bool:
    ref_url = urlparse(host_url)
    test_url = urlparse(urljoin(host_url, target))
    return test_url.scheme in ("http", "https") and (
        test_url.netloc == "" or test_url.netloc == ref_url.netloc
    )


class FlaskLoginUser:
    """Adapter that wraps a User for Flask-Login."""

    def __init__(
        self, orm_user: models.Member | models.Company | models.Accountant
    ) -> None:
        self.orm_user = orm_user

    def get_id(self) -> str:
        return self.orm_user.id

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def is_active(self) -> bool:
        return True

    @property
    def is_anonymous(self) -> bool:
        return False

    def __getattr__(self, name):
        return getattr(self.orm_user, name)


@dataclass
class FlaskSession:
    db: Database

    ROLES = {
        "member": UserRole.member,
        "company": UserRole.company,
        "accountant": UserRole.accountant,
    }

    def get_user_role(self) -> Optional[UserRole]:
        user_type = session.get("user_type")
        if user_type is None:
            return None
        return self.ROLES.get(user_type)

    def is_logged_in_as_member(self) -> bool:
        return session.get("user_type") == "member"

    def is_logged_in_as_company(self) -> bool:
        return session.get("user_type") == "company"

    def get_current_user(self) -> Optional[UUID]:
        try:
            return UUID(current_user.id)
        except AttributeError:
            return None

    def is_current_user_authenticated(self) -> bool:
        try:
            return current_user.is_authenticated
        except AttributeError:
            return False

    def login_member(self, member: UUID, remember: bool = False) -> None:
        member_orm = (
            self.db.session.query(models.Member)
            .filter(models.Member.id == (str(member)))
            .first()
        )
        assert member_orm
        login_user(FlaskLoginUser(member_orm), remember=remember)
        session["user_type"] = "member"

    def login_company(self, company: UUID, remember: bool = False) -> None:
        company_orm = (
            self.db.session.query(models.Company)
            .filter(models.Company.id == str(company))
            .first()
        )
        assert company_orm
        login_user(FlaskLoginUser(company_orm), remember=remember)
        session["user_type"] = "company"

    def login_accountant(self, accountant: UUID, remember: bool = False) -> None:
        accountant_orm = (
            self.db.session.query(models.Accountant)
            .filter(models.Accountant.id == str(accountant))
            .first()
        )
        assert accountant_orm
        login_user(FlaskLoginUser(accountant_orm), remember=remember)
        session["user_type"] = "accountant"

    def logout(self) -> None:
        session["user_type"] = None
        logout_user()

    def pop_next_url(self) -> Optional[str]:
        return session.pop("next", None)

    def set_next_url(self, next_url: str) -> None:
        if is_safe_url(next_url, request.base_url):
            session["next"] = next_url
