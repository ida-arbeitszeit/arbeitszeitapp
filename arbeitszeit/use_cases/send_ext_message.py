from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.mail_service import MailService
from arbeitszeit.repositories import ExternalMessageRepository


@dataclass
class SendExtMessageRequest:
    message_id: UUID


@dataclass
class SendExtMessageResponse:
    class RejectionReason(Exception, Enum):
        message_not_found = auto()
        message_could_not_be_sent = auto()

    rejection_reason: Optional[RejectionReason]

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@inject
@dataclass
class SendExtMessage:
    external_message_repository: ExternalMessageRepository
    mail_service: MailService

    def __call__(self, request: SendExtMessageRequest) -> SendExtMessageResponse:
        message = self.external_message_repository.get_by_id(request.message_id)
        if message is None:
            rejection_reason = SendExtMessageResponse.RejectionReason.message_not_found
            return SendExtMessageResponse(rejection_reason=rejection_reason)
        try:
            self.mail_service.send_message(
                subject=message.title,
                recipients=[message.receiver_adress],
                html=message.content_html,
                sender=message.sender_adress,
            )
        except Exception:
            rejection_reason = (
                SendExtMessageResponse.RejectionReason.message_could_not_be_sent
            )
            return SendExtMessageResponse(rejection_reason=rejection_reason)

        # to do: set message as sent in repositories
        return SendExtMessageResponse(rejection_reason=None)
