from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.email_notifications import (
    CompanyRegistration,
    EmailSender,
    MemberRegistration,
)
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class ResendConfirmationMailUseCase:
    @dataclass
    class Request:
        user: UUID

    @dataclass
    class Response:
        is_token_sent: bool = False

    email_sender: EmailSender
    database: DatabaseGateway

    def resend_confirmation_mail(self, request: Request) -> Response:
        member_record = (
            self.database.get_members()
            .with_id(request.user)
            .joined_with_email_address()
            .first()
        )
        if member_record is not None:
            _, email = member_record
            if email.confirmed_on is None:
                self.email_sender.send_email(
                    MemberRegistration(email_address=email.address)
                )
                return self.Response(is_token_sent=True)
        company_record = (
            self.database.get_companies()
            .with_id(request.user)
            .joined_with_email_address()
            .first()
        )
        if company_record is not None:
            _, email = company_record
            if email.confirmed_on is None:
                self.email_sender.send_email(
                    CompanyRegistration(email_address=email.address)
                )
                return self.Response(is_token_sent=True)
        return self.Response()
