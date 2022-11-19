from dataclasses import dataclass
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import CompanyRepository, MemberRepository
from arbeitszeit.token import (
    CompanyRegistrationMessagePresenter,
    MemberRegistrationMessagePresenter,
    TokenService,
)


@inject
@dataclass
class ResendConfirmationMailUseCase:
    @dataclass
    class Request:
        user: UUID

    @dataclass
    class Response:
        is_token_sent: bool = False

    company_repository: CompanyRepository
    company_registration_message_presenter: CompanyRegistrationMessagePresenter
    member_repository: MemberRepository
    member_registration_message_presenter: MemberRegistrationMessagePresenter
    token_service: TokenService

    def resend_confirmation_mail(self, request: Request) -> Response:
        member = self.member_repository.get_members().with_id(request.user).first()
        if member and member.confirmed_on is None:
            token = self.token_service.generate_token(member.email)
            self.member_registration_message_presenter.show_member_registration_message(
                request.user,
                token=token,
            )
            return self.Response(is_token_sent=True)
        if (
            company := self.company_repository.get_by_id(request.user)
        ) and company.confirmed_on is None:
            token = self.token_service.generate_token(company.email)
            self.company_registration_message_presenter.show_company_registration_message(
                company=company.id,
                token=token,
            )
            return self.Response(is_token_sent=True)
        return self.Response()
