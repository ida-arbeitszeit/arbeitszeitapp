from dataclasses import dataclass

from arbeitszeit.presenters import AccountantInvitationPresenter
from arbeitszeit.repositories import AccountantRepository


@dataclass
class SendAccountantRegistrationTokenUseCase:
    class Response:
        pass

    @dataclass
    class Request:
        email: str

    invitation_presenter: AccountantInvitationPresenter
    accountant_repository: AccountantRepository

    def send_accountant_registration_token(self, request: Request) -> Response:
        if not self._is_user_existing(request.email):
            self.invitation_presenter.send_accountant_invitation(email=request.email)
        return self.Response()

    def _is_user_existing(self, email: str) -> bool:
        return bool(
            self.accountant_repository.get_accountants().with_email_address(email)
        )
