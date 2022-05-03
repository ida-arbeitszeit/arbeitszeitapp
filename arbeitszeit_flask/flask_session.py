from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from flask import session
from flask_login import current_user, login_user

from arbeitszeit_flask.database.repositories import MemberRepository


@dataclass
class FlaskSession:
    member_repository: MemberRepository

    def get_current_user(self) -> Optional[UUID]:
        try:
            return UUID(current_user.id)
        except AttributeError:
            return None

    def login_member(self, email: str) -> None:
        member = self.member_repository.get_member_orm_by_mail(email)
        session["user_type"] = "member"
        login_user(member)
