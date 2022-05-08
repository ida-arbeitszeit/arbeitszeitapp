from dataclasses import dataclass

from injector import inject

from arbeitszeit.repositories import CompanyRepository, MemberRepository
from arbeitszeit.token import TokenService

from .accountant_invitation_presenter import AccountantInvitationPresenter


@inject
@dataclass
class SendAccountantRegistrationTokenUseCase:
    class Response:
        pass

    @dataclass
    class Request:
        email: str

    invitation_presenter: AccountantInvitationPresenter
    token_service: TokenService
    member_repository: MemberRepository
    company_repository: CompanyRepository

    def send_accountant_registration_token(self, request: Request) -> Response:
        if not self._is_user_existing(request.email):
            token = self.token_service.generate_token(request.email)
            self.invitation_presenter.send_accountant_invitation(
                token=token, email=request.email
            )
        return self.Response()

    def _is_user_existing(self, email: str) -> bool:
        return self.member_repository.has_member_with_email(
            email
        ) or self.company_repository.has_company_with_email(email)
