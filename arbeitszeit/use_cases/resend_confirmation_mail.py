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
        member = self.database.get_members().with_id(request.user).first()
        if member and member.confirmed_on is None:
            self.member_registration_message_presenter.show_member_registration_message(
                member.email,
            )
            return self.Response(is_token_sent=True)
        if (
            company := self.database.get_companies().with_id(request.user).first()
        ) and company.confirmed_on is None:
            self.company_registration_message_presenter.show_company_registration_message(
                company.email,
            )
            return self.Response(is_token_sent=True)
        return self.Response()
