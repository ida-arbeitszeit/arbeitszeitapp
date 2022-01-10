from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.user_action import UserActionType


@dataclass(frozen=True)
class FakeUserAction:
    action_type: UserActionType
    reference: UUID

    def get_type(self) -> UserActionType:
        return self.action_type

    def get_reference(self) -> UUID:
        return self.reference
