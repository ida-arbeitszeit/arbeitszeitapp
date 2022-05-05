from typing import Optional
from uuid import UUID


class FakeSession:
    def __init__(self) -> None:
        self._current_user_id: Optional[UUID] = None
        self._is_logged_in = False

    def is_logged_in(self) -> bool:
        return self._is_logged_in

    def set_current_user_id(self, user_id: Optional[UUID]) -> None:
        self._current_user_id = user_id

    def get_current_user(self) -> Optional[UUID]:
        return self._current_user_id

    def login_member(self, email: str, remember: bool = False) -> None:
        self._is_logged_in = True

    def login_company(self, email: str, remember: bool = False) -> None:
        self._is_logged_in = True

    def logout(self) -> None:
        self._is_logged_in = False
