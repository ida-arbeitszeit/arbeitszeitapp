from dataclasses import dataclass

from injector import inject

from arbeitszeit.accountant_notifications import Notification
from arbeitszeit_web.email import EmailConfiguration, MailService, UserAddressBook
from arbeitszeit_web.text_renderer import TextRenderer
from arbeitszeit_web.translator import Translator


@inject
@dataclass
class NotifyAccountantsAboutNewPlanPresenterImpl:
    email_sender: MailService
    address_book: UserAddressBook
    translator: Translator
    email_configuration: EmailConfiguration
    text_renderer: TextRenderer

    def notify_accountant_about_new_plan(self, notification: Notification) -> None:
        recipient = self.address_book.get_user_email_address(notification.accountant_id)
        if not recipient:
            return
        self.email_sender.send_message(
            self.translator.gettext("Plan was filed"),
            [recipient],
            self.text_renderer.render_accountant_notification_about_new_plan(
                product_name=notification.product_name,
            ),
            self.email_configuration.get_sender_address(),
        )
