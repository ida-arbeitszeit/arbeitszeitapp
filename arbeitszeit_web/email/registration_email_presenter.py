from dataclasses import dataclass

from arbeitszeit_web.email import EmailConfiguration, MailService
from arbeitszeit_web.text_renderer import TextRenderer
from arbeitszeit_web.token import TokenService
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class RegistrationEmailPresenter:
    email_sender: MailService
    url_index: UrlIndex
    email_configuration: EmailConfiguration
    translator: Translator
    text_renderer: TextRenderer
    token_service: TokenService

    def show_member_registration_message(self, email_address: str) -> None:
        token = self.token_service.generate_token(email_address)
        self._show_registration_message(
            email_address=email_address,
            content=self.text_renderer.render_member_registration_message(
                confirmation_url=self.url_index.get_member_confirmation_url(token=token)
            ),
        )

    def show_company_registration_message(self, email_address: str) -> None:
        token = self.token_service.generate_token(email_address)
        self._show_registration_message(
            email_address=email_address,
            content=self.text_renderer.render_company_registration_message(
                confirmation_url=self.url_index.get_company_confirmation_url(
                    token=token
                )
            ),
        )

    def _show_registration_message(self, *, email_address: str, content: str) -> None:
        self.email_sender.send_message(
            self.translator.gettext("Account confirmation"),
            [email_address],
            content,
            self.email_configuration.get_sender_address(),
        )
