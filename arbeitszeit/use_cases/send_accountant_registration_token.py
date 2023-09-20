from dataclasses import dataclass

from arbeitszeit.email_notifications import AccountantInvitation, EmailSender
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class SendAccountantRegistrationTokenUseCase:
    class Response:
        pass

    @dataclass
    class Request:
        email: str

    email_sender: EmailSender
    database: DatabaseGateway

    def send_accountant_registration_token(self, request: Request) -> Response:
        if not self._is_user_existing(request.email):
            self.email_sender.send_email(
                AccountantInvitation(email_address=request.email)
            )
        return self.Response()

    def _is_user_existing(self, email: str) -> bool:
        return bool(self.database.get_accountants().with_email_address(email))
