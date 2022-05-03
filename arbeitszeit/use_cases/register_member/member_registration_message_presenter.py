from typing import Protocol
from uuid import UUID


class MemberRegistrationMessagePresenter(Protocol):
    def show_member_registration_message(self, member: UUID, token: str) -> None:
        ...
