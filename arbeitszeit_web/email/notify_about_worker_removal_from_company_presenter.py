from dataclasses import dataclass

from arbeitszeit.email_notifications import WorkerRemovalNotification
from arbeitszeit_web.email import EmailConfiguration, MailService
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class NotifyAboutWorkerRemovalPresenter:
    email_service: MailService
    email_configuration: EmailConfiguration
    translator: Translator
    url_index: UrlIndex

    def notify(self, message_data: WorkerRemovalNotification) -> None:
        self.email_service.send_message(
            subject=self.translator.gettext("Worker removed from company"),
            recipients=[message_data.worker_email, message_data.company_email],
            html=self.translator.gettext(
                f"Hello,<br><br>The worker {message_data.worker_name} (id: {str(message_data.worker_id)}) has been removed from company {message_data.company_name}."
            ),
            sender=self.email_configuration.get_sender_address(),
        )
