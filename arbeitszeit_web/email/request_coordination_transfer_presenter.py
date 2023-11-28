from dataclasses import dataclass
from html import escape

from arbeitszeit.email_notifications import CoordinationTransferRequest
from arbeitszeit_web.email import EmailConfiguration, MailService
from arbeitszeit_web.translator import Translator


@dataclass
class RequestCoordinationTransferEmailPresenter:
    translator: Translator
    mail_service: MailService
    email_configuration: EmailConfiguration

    def present(self, email: CoordinationTransferRequest) -> None:
        self.mail_service.send_message(
            subject=self.translator.gettext(
                "You are asked to be the coordinator of a cooperation"
            ),
            recipients=[email.candidate_email],
            html=self.translator.gettext(
                "Hello %(candidate)s,<br>Your are asked to be the coordinator of the cooperation '%(cooperation)s'. Please check the request in the Arbeitszeitapp."
            )
            % dict(
                candidate=escape(email.candidate_name),
                cooperation=escape(email.cooperation_name),
            ),
            sender=self.email_configuration.get_sender_address(),
        )
