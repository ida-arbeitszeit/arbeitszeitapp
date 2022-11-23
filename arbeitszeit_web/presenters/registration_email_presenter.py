from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from injector import inject

from arbeitszeit_web.email import EmailConfiguration, MailService, UserAddressBook
from arbeitszeit_web.text_renderer import TextRenderer
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


class RegistrationEmailTemplate(Protocol):
    def render_to_html(self, confirmation_url: str) -> str:
        ...


@inject
@dataclass
class RegistrationEmailPresenter:
    email_sender: MailService
    address_book: UserAddressBook
    url_index: UrlIndex
    email_configuration: EmailConfiguration
    translator: Translator
    text_renderer: TextRenderer

    def show_member_registration_message(self, member: UUID, token: str) -> None:
        self._show_registration_message(
            member,
            content=self.text_renderer.render_member_registration_message(
                confirmation_url=self.url_index.get_member_confirmation_url(token=token)
            ),
        )

    def show_company_registration_message(self, company: UUID, token: str) -> None:
        self._show_registration_message(
            company,
            self.text_renderer.render_company_registration_message(
                confirmation_url=self.url_index.get_company_confirmation_url(
                    token=token
                )
            ),
        )

    def _show_registration_message(self, user: UUID, content: str) -> None:
        recipient = self.address_book.get_user_email_address(user)
        assert recipient
        self.email_sender.send_message(
            self.translator.gettext("Account confirmation"),
            [recipient],
            content,
            self.email_configuration.get_sender_address(),
        )
