from dataclasses import dataclass

from injector import inject

from arbeitszeit.token import TokenService


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

    token_service: TokenService

    def register_accountant(self, request: Request) -> Response:
        invited_email = self.token_service.confirm_token(
            request.token, max_age_in_sec=1
        )
        return self.Response(is_accepted=invited_email == request.email)
