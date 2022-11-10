from typing import Optional, Protocol
from uuid import UUID


class TokenService(Protocol):
    def generate_token(self, input: str) -> str:
        ...


class InvitationTokenValidator(Protocol):
    def unwrap_invitation_token(self, token: str) -> Optional[str]:
        ...


class MemberRegistrationMessagePresenter(Protocol):
    def show_member_registration_message(self, member: UUID, token: str) -> None:
        ...


class CompanyRegistrationMessagePresenter(Protocol):
    def show_company_registration_message(self, company: UUID, token: str) -> None:
        ...
