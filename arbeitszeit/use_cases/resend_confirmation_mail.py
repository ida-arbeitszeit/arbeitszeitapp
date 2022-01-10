from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from injector import inject

from arbeitszeit.errors import CannotSendEmail
from arbeitszeit.mail_service import MailService
from arbeitszeit.token import TokenService


@dataclass
class ResendConfirmationMailResponse:
    class RejectionReason(Exception, Enum):
        sending_mail_failed = auto()

    rejection_reason: Optional[RejectionReason]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@dataclass
class ResendConfirmationMailRequest:
    subject: str
    recipient: str
    sender: str
    template_name: str
    endpoint: str


@inject
@dataclass
class ResendConfirmationMail:
    mail_service: MailService
    token_service: TokenService

    def __call__(
        self, request: ResendConfirmationMailRequest
    ) -> ResendConfirmationMailResponse:
        html = self._create_confirmation_mail(request)
        try:
            self.mail_service.send_message(
                subject=request.subject,
                recipients=[request.recipient],
                html=html,
                sender=request.sender,
            )
        except CannotSendEmail:
            return ResendConfirmationMailResponse(
                rejection_reason=ResendConfirmationMailResponse.RejectionReason.sending_mail_failed
            )
        return ResendConfirmationMailResponse(rejection_reason=None)

    def _create_confirmation_mail(self, request: ResendConfirmationMailRequest) -> str:
        token = self.token_service.generate_token(request.recipient)
        html = self.mail_service.create_confirmation_html(
            request.template_name, request.endpoint, token
        )
        return html
