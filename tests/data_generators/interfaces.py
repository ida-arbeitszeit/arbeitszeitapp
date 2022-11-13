from typing import Optional, Protocol
from uuid import UUID


class TokenInbox(Protocol):
    def get_deliviered_member_token(self, member: UUID) -> Optional[str]:
        ...
