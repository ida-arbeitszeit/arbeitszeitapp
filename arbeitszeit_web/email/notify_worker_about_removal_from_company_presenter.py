from dataclasses import dataclass

from arbeitszeit_web.email import EmailConfiguration, MailService
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class NotifyWorkerAboutRemovalPresenter:
    email_service: MailService
    email_configuration: EmailConfiguration
    translator: Translator
    url_index: UrlIndex

    def notify(self, worker_email: str, company_name: str) -> None:
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
