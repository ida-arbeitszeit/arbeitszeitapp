from dataclasses import dataclass

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.email_notifications import EmailSender, ResetPasswordConfirmation
from arbeitszeit.password_hasher import PasswordHasher
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class Request:
    email_address: str
    new_password: str


@dataclass
class Response:
    is_changed: bool


@dataclass
class ChangeUserPasswordUseCase:
    database: DatabaseGateway
    password_hasher: PasswordHasher
    email_sender: EmailSender

    def change_user_password(self, request: Request) -> Response:
        account_credentials_query = (
            self.database.get_account_credentials().with_email_address(
                request.email_address.strip()
            )
        )

        if not account_credentials_query.first():
            return Response(is_changed=False)

        row_update_count = (
            account_credentials_query.update()
            .change_password_hash(
                self.password_hasher.calculate_password_hash(request.new_password)
            )
            .perform()
        )

        if row_update_count > 0:
            self.email_sender.send_email(
                ResetPasswordConfirmation(email_address=request.email_address)
            )
            return Response(is_changed=True)

        return Response(is_changed=False)
