from dataclasses import dataclass
from typing import List

from arbeitszeit.token import ConfirmationEmail
from arbeitszeit_web.email import EmailConfiguration
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import ConfirmationUrlIndex


@dataclass
class SendConfirmationEmailPresenter:
    @dataclass
    class ViewModel:
        subject: str
        recipients: List[str]
        sender: str
        confirmation_url: str

    url_index: ConfirmationUrlIndex
    email_configuration: EmailConfiguration
    translator: Translator

    def render_confirmation_email(self, email: ConfirmationEmail) -> ViewModel:
        return self.ViewModel(
            confirmation_url=self.url_index.get_confirmation_url(email.token),
            subject=self.translator.gettext("Please confirm your account"),
            recipients=[email.email],
            sender=self.email_configuration.get_sender_address(),
        )
