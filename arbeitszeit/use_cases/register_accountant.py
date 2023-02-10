from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from arbeitszeit.repositories import AccountantRepository
from arbeitszeit.token import InvitationTokenValidator


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
        email_address: str

    token_service: InvitationTokenValidator
    accountant_repository: AccountantRepository

    def register_accountant(self, request: Request) -> Response:
        invited_email = self.token_service.unwrap_invitation_token(request.token)
        if invited_email != request.email:
            return self._failed_registration(request)
        if self.accountant_repository.has_accountant_with_email(request.email):
            return self._failed_registration(request)
        user_id = self.accountant_repository.create_accountant(
            email=request.email,
            name=request.name,
            password=request.password,
        )
        return self.Response(
            is_accepted=True, user_id=user_id, email_address=request.email
        )

    def _failed_registration(self, request: Request) -> Response:
        return self.Response(
            is_accepted=False,
            user_id=None,
            email_address=request.email,
        )
