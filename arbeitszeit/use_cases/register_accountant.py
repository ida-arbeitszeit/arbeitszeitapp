from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import (
    AccountantRepository,
    CompanyRepository,
    MemberRepository,
)
from arbeitszeit.token import InvitationTokenValidator


@inject
@dataclass
class RegisterAccountantUseCase:
    @dataclass
    class Request:
        token: str
        email: str
        name: str
        password: str

    @dataclass
    class Response:
        is_accepted: bool
        user_id: Optional[UUID]

    token_service: InvitationTokenValidator
    member_repository: MemberRepository
    company_repository: CompanyRepository
    accountant_repository: AccountantRepository

    def register_accountant(self, request: Request) -> Response:
        invited_email = self.token_service.unwrap_invitation_token(request.token)
        if invited_email != request.email:
            return self._failed_registration()
        if self.member_repository.has_member_with_email(request.email):
            return self._failed_registration()
        if self.company_repository.has_company_with_email(request.email):
            return self._failed_registration()
        if self.accountant_repository.has_accountant_with_email(request.email):
            return self._failed_registration()
        user_id = self.accountant_repository.create_accountant(
            email=request.email,
            name=request.name,
            password=request.password,
        )
        return self.Response(is_accepted=True, user_id=user_id)

    def _failed_registration(self) -> Response:
        return self.Response(is_accepted=False, user_id=None)
