from typing import Optional, Protocol
from uuid import UUID


class Session(Protocol):
    def get_current_user(self) -> Optional[UUID]:
        ...

    def login_member(self, email: str, remember: bool = ...) -> None:
        ...

    def login_company(self, email: str, remember: bool = ...) -> None:
        ...

    def login_accountant(self, email: str, remember: bool = ...) -> None:
        ...

    def pop_next_url(self) -> Optional[str]:
        ...
