from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional
from uuid import UUID

from arbeitszeit_web.session import UserRole


class FakeSession:
    @dataclass
    class LoginAttempt:
        user_role: UserRole
        user_id: UUID
        is_remember: bool

    def __init__(self) -> None:
        self._current_user_id: Optional[UUID] = None
        self._recent_logins: List[FakeSession.LoginAttempt] = []
        self._next_url: Optional[str] = None
        self._current_user_role: Optional[UserRole] = None

    def get_user_role(self) -> Optional[UserRole]:
        return self._current_user_role

    def is_logged_in(self) -> bool:
        return self._current_user_role is not None

    def get_current_user(self) -> Optional[UUID]:
        return self._current_user_id

    def login_member(self, member: UUID, remember: bool = False) -> None:
        self._current_user_id = member
        self._recent_logins.append(
            self.LoginAttempt(
                user_role=UserRole.member,
                user_id=member,
                is_remember=remember,
            )
        )
        self._current_user_role = UserRole.member

    def login_company(self, company: UUID, remember: bool = False) -> None:
        self._current_user_id = company
        self._recent_logins.append(
            self.LoginAttempt(
                user_role=UserRole.company,
                user_id=company,
                is_remember=remember,
            )
        )
        self._current_user_role = UserRole.company

    def login_accountant(self, accountant: UUID, remember: bool = False) -> None:
        self._current_user_id = accountant
        self._recent_logins.append(
            self.LoginAttempt(
                user_role=UserRole.accountant,
                user_id=accountant,
                is_remember=remember,
            )
        )
        self._current_user_role = UserRole.accountant

    def get_most_recent_login(self) -> Optional[LoginAttempt]:
        if not self._recent_logins:
            return None
        else:
            return self._recent_logins[-1]

    def set_next_url(self, url: Optional[str]) -> None:
        self._next_url = url

    def pop_next_url(self) -> Optional[str]:
        next_url = self._next_url
        self._next_url = None
        return next_url

    def logout(self) -> None:
        self._current_user_role = None
        self._current_user_id = None
