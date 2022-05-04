from typing import Optional
from uuid import UUID


class FakeSession:
    def __init__(self) -> None:
        self._current_user_id: Optional[UUID] = None

    def set_current_user_id(self, user_id: Optional[UUID]) -> None:
        self._current_user_id = user_id

    def get_current_user(self) -> Optional[UUID]:
        return self._current_user_id

    def login_member(self, email: str, remember: bool = False) -> None:
        pass
