import enum
from typing import Protocol
from uuid import UUID


class UserActionType(enum.Enum):
    answer_invite = 1
    answer_cooperation_request = 2


class UserAction(Protocol):
    def get_type(self) -> UserActionType:
        ...

    def get_reference(self) -> UUID:
        ...
