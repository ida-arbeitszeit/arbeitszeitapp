from dataclasses import dataclass
from uuid import UUID

from arbeitszeit_web.email import EmailConfiguration, MailService
from arbeitszeit_web.text_renderer import TextRenderer
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class InviteWorkerPresenterImpl:
    email_service: MailService
    email_configuration: EmailConfiguration
    text_renderer: TextRenderer
    translator: Translator
    url_index: UrlIndex

    def show_invite_worker_message(self, worker_email: str, invite: UUID) -> None:
        invitation_url = self.url_index.get_answer_company_work_invite_url(
            invite_id=invite
        )
        self.email_service.send_message(
            subject=self.translator.gettext(
                "Invitation from a company on Arbeitszeitapp"
            ),
            recipients=[worker_email],
            html=self.text_renderer.render_member_notfication_about_work_invitation(
                invitation_url=invitation_url
            ),
            sender=self.email_configuration.get_sender_address(),
        )
