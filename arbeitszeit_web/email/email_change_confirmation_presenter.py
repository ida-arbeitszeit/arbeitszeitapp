from dataclasses import dataclass

from arbeitszeit import email_notifications
from arbeitszeit_web.email import EmailConfiguration, MailService
from arbeitszeit_web.text_renderer import TextRenderer
from arbeitszeit_web.token import TokenService
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class EmailChangeConfirmationPresenter:
    email_service: MailService
    token_service: TokenService
    text_renderer: TextRenderer
    url_index: UrlIndex
    translator: Translator
    email_configuration: EmailConfiguration

    def present_email_change_confirmation(
        self, email_change_confirmation: email_notifications.EmailChangeConfirmation
    ) -> None:
        self.email_service.send_message(
            subject=self.translator.gettext("Email address change requested"),
            sender=self.email_configuration.get_sender_address(),
            html=self.text_renderer.render_email_change_notification(
                change_email_url=self.url_index.get_change_email_url(
                    token=self.token_service.generate_token(
                        "{old_email}:{new_email}".format(
                            old_email=email_change_confirmation.old_email_address,
                            new_email=email_change_confirmation.new_email_address,
                        )
                    )
                )
            ),
            recipients=[email_change_confirmation.new_email_address],
        )
