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
        self._notify_worker(
            worker_email=message_data.worker_email,
            company_name=message_data.company_name,
        )
        self._notify_company(
            company_email=message_data.company_email,
            worker_name=message_data.worker_name,
            worker_id=message_data.worker_id,
        )

    def _notify_company(
        self, company_email: str, worker_name: str, worker_id: str
    ) -> None:
        self.email_service.send_message(
            subject=self.translator.gettext(
                "You have removed a worker from your company"
            ),
            recipients=[company_email],
            html=self.translator.gettext(
                f"Hello,<br><br>You have removed worker {worker_name} (id: {worker_id}) from your company."
            ),
            sender=self.email_configuration.get_sender_address(),
        )

    def _notify_worker(self, worker_email: str, company_name: str) -> None:
        self.email_service.send_message(
            subject=self.translator.gettext(
                "You have been removed as worker from a company"
            ),
            recipients=[worker_email],
            html=self.translator.gettext(
                f"Hello,<br><br>You have been removed as worker from the company {company_name}."
            ),
            sender=self.email_configuration.get_sender_address(),
        )
