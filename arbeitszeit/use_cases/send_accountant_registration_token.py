from dataclasses import dataclass

from injector import inject

from arbeitszeit.token import ConfirmationEmail, TokenDeliverer, TokenService


@inject
@dataclass
class SendAccountantRegistrationTokenUseCase:
    class Response:
        pass

    @dataclass
    class Request:
        email: str

    token_deliverer: TokenDeliverer
    token_service: TokenService

    def send_accountant_registration_token(self, request: Request) -> Response:
        token = self.token_service.generate_token(request.email)
        self.token_deliverer.deliver_confirmation_token(
            ConfirmationEmail(token=token, email="test@test.test")
        )
        return self.Response()
