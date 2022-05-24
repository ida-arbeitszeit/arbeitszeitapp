from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from flask import session
from flask_login import current_user, login_user, logout_user

from arbeitszeit_flask.database.repositories import (
    AccountantRepository,
    CompanyRepository,
    MemberRepository,
)


@dataclass
class FlaskSession:
    member_repository: MemberRepository
    company_repository: CompanyRepository
    accountant_repository: AccountantRepository

    def is_logged_in_as_member(self) -> bool:
        return session.get("user_type") == "member"

    def is_logged_in_as_company(self) -> bool:
        return session.get("user_type") == "company"

    def get_current_user(self) -> Optional[UUID]:
        try:
            return UUID(current_user.id)
        except AttributeError:
            return None

    def login_member(self, email: str, remember: bool = False) -> None:
        member = self.member_repository.get_member_orm_by_mail(email)
        login_user(member, remember=remember)
        session["user_type"] = "member"

    def login_company(self, email: str, remember: bool = False) -> None:
        company = self.company_repository.get_company_orm_by_mail(email)
        login_user(company, remember=remember)
        session["user_type"] = "company"

    def login_accountant(self, email: str, remember: bool = False) -> None:
        accountant = self.accountant_repository.get_accountant_orm_by_mail(email)
        login_user(accountant, remember=remember)
        session["user_type"] = "accountant"

    def logout(self) -> None:
        session["user_type"] = None
        logout_user()
