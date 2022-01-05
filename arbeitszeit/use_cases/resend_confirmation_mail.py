from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from injector import inject

from arbeitszeit.mail_service import MailService


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
    html: str
    recipient: str
    sender: str


@inject
@dataclass
class ResendConfirmationMail:
    mail_service: MailService

    def __call__(
        self, request: ResendConfirmationMailRequest
    ) -> ResendConfirmationMailResponse:
        try:
            self.mail_service.send_message(
                subject=request.subject,
                recipients=[request.recipient],
                html=request.html,
                sender=request.sender,
            )
        except Exception:
            return ResendConfirmationMailResponse(
                rejection_reason=ResendConfirmationMailResponse.RejectionReason.sending_mail_failed
            )
        return ResendConfirmationMailResponse(rejection_reason=None)
