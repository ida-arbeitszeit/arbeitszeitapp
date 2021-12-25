from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from injector import inject

from arbeitszeit.mail_service import MailService
from arbeitszeit.repositories import SentExternalMessageRepository


@dataclass
class SendExtMessageRequest:
    sender_adress: str
    receiver_adress: str
    title: str
    content_html: str


@dataclass
class SendExtMessageResponse:
    class RejectionReason(Exception, Enum):
        message_could_not_be_sent = auto()

    rejection_reason: Optional[RejectionReason]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@inject
@dataclass
class SendExtMessage:
    sent_external_message_repository: SentExternalMessageRepository
    mail_service: MailService

    def __call__(self, request: SendExtMessageRequest) -> SendExtMessageResponse:
        try:
            self.mail_service.send_message(
                subject=request.title,
                recipients=[request.receiver_adress],
                html=request.content_html,
                sender=request.sender_adress,
            )
        except Exception:
            rejection_reason = (
                SendExtMessageResponse.RejectionReason.message_could_not_be_sent
            )
            return SendExtMessageResponse(rejection_reason=rejection_reason)

        # to do: set message as sent in repositories
        return SendExtMessageResponse(rejection_reason=None)
