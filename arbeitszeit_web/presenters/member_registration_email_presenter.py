from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from arbeitszeit_web.email import EmailConfiguration, MailService, UserAddressBook
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import ConfirmationUrlIndex


class MemberRegistrationEmailTemplate(Protocol):
    def render_to_html(self, confirmation_url: str) -> str:
        ...


@dataclass
class MemberRegistrationEmailPresenter:
    email_sender: MailService
    address_book: UserAddressBook
    email_template: MemberRegistrationEmailTemplate
    url_index: ConfirmationUrlIndex
    email_configuration: EmailConfiguration
    translator: Translator

    def show_member_registration_message(self, member: UUID, token: str) -> None:
        confirmation_url = self.url_index.get_confirmation_url(token)
        mail_content = self.email_template.render_to_html(confirmation_url)
        recipient = self.address_book.get_user_email_address(member)
        assert recipient
        self.email_sender.send_message(
            self.translator.gettext("Account confirmation"),
            [recipient],
            mail_content,
            self.email_configuration.get_sender_address(),
        )
