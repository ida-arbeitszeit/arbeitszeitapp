from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse
from uuid import UUID

from flask import request, session
from flask_login import current_user, login_user, logout_user
from is_safe_url import is_safe_url

from arbeitszeit_flask import models
from arbeitszeit_flask.database.repositories import (
    AccountantRepository,
    CompanyRepository,
    MemberRepository,
)
from arbeitszeit_web.session import UserRole


@dataclass
class FlaskSession:
    member_repository: MemberRepository
    company_repository: CompanyRepository
    accountant_repository: AccountantRepository

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

    def login_member(self, member: UUID, remember: bool = False) -> None:
        member = models.Member.query.get(str(member))
        login_user(member, remember=remember)
        session["user_type"] = "member"

    def login_company(self, company: UUID, remember: bool = False) -> None:
        company = models.Company.query.get(str(company))
        login_user(company, remember=remember)
        session["user_type"] = "company"

    def login_accountant(self, accountant: UUID, remember: bool = False) -> None:
        accountant = models.Accountant.query.get(str(accountant))
        login_user(accountant, remember=remember)
        session["user_type"] = "accountant"

    def logout(self) -> None:
        session["user_type"] = None
        logout_user()

    def pop_next_url(self) -> Optional[str]:
        return session.pop("next", None)

    def set_next_url(self, next_url: str) -> None:
        hostname = urlparse(request.base_url).netloc
        if is_safe_url(next_url, {hostname}):
            session["next"] = next_url
