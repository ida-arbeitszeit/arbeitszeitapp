from dataclasses import dataclass

from arbeitszeit_web.email import EmailConfiguration, MailService
from arbeitszeit_web.text_renderer import TextRenderer
from arbeitszeit_web.translator import Translator


@dataclass
class InviteWorkerPresenterImpl:
    email_service: MailService
    email_configuration: EmailConfiguration
    text_renderer: TextRenderer
    translator: Translator

    def show_invite_worker_message(self, worker_email: str) -> None:
        self.email_service.send_message(
            subject=self.translator.gettext(
                "Invitation from a company on Arbeitszeitapp"
            ),
            recipients=[worker_email],
            html=self.text_renderer.render_member_notfication_about_work_invitation(),
            sender=self.email_configuration.get_sender_address(),
        )
