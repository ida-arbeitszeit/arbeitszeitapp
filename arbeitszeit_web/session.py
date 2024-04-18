import enum
from typing import Optional, Protocol
from uuid import UUID


@enum.unique
class UserRole(enum.Enum):
    member = enum.auto()
    company = enum.auto()
    accountant = enum.auto()


class Session(Protocol):
    def get_current_user(self) -> Optional[UUID]: ...

    def login_member(self, member: UUID, remember: bool = ...) -> None: ...

    def login_company(self, company: UUID, remember: bool = ...) -> None: ...

    def login_accountant(self, accountant: UUID, remember: bool = ...) -> None: ...

    def logout(self) -> None: ...

    def pop_next_url(self) -> Optional[str]: ...

    def set_next_url(self, next_url: str) -> None: ...

    def get_user_role(self) -> Optional[UserRole]: ...
