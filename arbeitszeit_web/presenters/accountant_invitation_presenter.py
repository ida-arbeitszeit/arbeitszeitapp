from dataclasses import dataclass
from typing import List, Protocol

from arbeitszeit_web.email import EmailConfiguration
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import AccountantInvitationUrlIndex


@dataclass
class ViewModel:
    subject: str
    recipients: List[str]
    sender: str
    registration_link_url: str


class AccountantInvitationEmailView(Protocol):
    def render_accountant_invitation_email(self, view_model: ViewModel) -> None:
        ...


@dataclass
class AccountantInvitationEmailPresenter:
    invitation_view: AccountantInvitationEmailView
    email_configuration: EmailConfiguration
    translator: Translator
    invitation_url_index: AccountantInvitationUrlIndex

    def send_accountant_invitation(self, email: str, token: str) -> None:
        view_model = ViewModel(
            subject=self.translator.gettext("Invitation to Arbeitszeitapp"),
            recipients=[email],
            sender=self.email_configuration.get_sender_address(),
            registration_link_url=self.invitation_url_index.get_accountant_invitation_url(
                token
            ),
        )
        self.invitation_view.render_accountant_invitation_email(view_model)
