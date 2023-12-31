from dataclasses import dataclass
from html import escape

from arbeitszeit.email_notifications import CoordinationTransferRequest
from arbeitszeit_web.email import EmailConfiguration, MailService
from arbeitszeit_web.translator import Translator
from arbeitszeit_web.url_index import UrlIndex


@dataclass
class RequestCoordinationTransferEmailPresenter:
    translator: Translator
    mail_service: MailService
    email_configuration: EmailConfiguration
    url_index: UrlIndex

    def present(self, email: CoordinationTransferRequest) -> None:
        self.mail_service.send_message(
            subject=self.translator.gettext(
                "You are asked to be the coordinator of a cooperation"
            ),
            recipients=[email.candidate_email],
            html=self.translator.gettext(
                "Hello %(candidate)s,<br>Your are asked to be the coordinator of the cooperation '%(cooperation)s'. Please follow this link to check the request in the Arbeitszeitapp: <a href='%(url)s'>LINK</a>."
            )
            % dict(
                candidate=escape(email.candidate_name),
                cooperation=escape(email.cooperation_name),
                url=self.url_index.get_show_coordination_transfer_request_url(
                    email.transfer_request
                ),
            ),
            sender=self.email_configuration.get_sender_address(),
        )
