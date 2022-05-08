from dataclasses import dataclass

from injector import inject

from arbeitszeit.token import InvitationTokenValidator


@inject
@dataclass
class RegisterAccountantUseCase:
    @dataclass
    class Request:
        token: str
        email: str
        name: str

    @dataclass
    class Response:
        is_accepted: bool

    token_service: InvitationTokenValidator

    def register_accountant(self, request: Request) -> Response:
        invited_email = self.token_service.unwrap_invitation_token(request.token)
        return self.Response(is_accepted=invited_email == request.email)
