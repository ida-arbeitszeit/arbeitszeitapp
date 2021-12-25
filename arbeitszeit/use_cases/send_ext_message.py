from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

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
    sent_message: Optional[UUID]

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
            return SendExtMessageResponse(
                rejection_reason=rejection_reason, sent_message=None
            )
        sent_message_id = self.sent_external_message_repository.save_sent_message(
            title=request.title,
            sender_adress=request.sender_adress,
            receiver_adress=request.receiver_adress,
            content_html=request.content_html,
        )
        return SendExtMessageResponse(
            rejection_reason=None, sent_message=sent_message_id
        )
