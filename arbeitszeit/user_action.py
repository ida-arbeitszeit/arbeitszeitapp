import enum
from dataclasses import dataclass
from uuid import UUID


class UserActionType(enum.Enum):
    answer_invite = 1
    answer_cooperation_request = 2


@dataclass
class UserAction:
    type: UserActionType
    reference: UUID
