from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.presenters import (
    CompanyRegistrationMessagePresenter,
    MemberRegistrationMessagePresenter,
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

    company_registration_message_presenter: CompanyRegistrationMessagePresenter
    member_registration_message_presenter: MemberRegistrationMessagePresenter
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
                self.member_registration_message_presenter.show_member_registration_message(
                    email.address,
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
                self.company_registration_message_presenter.show_company_registration_message(
                    email.address,
                )
                return self.Response(is_token_sent=True)
        return self.Response()
