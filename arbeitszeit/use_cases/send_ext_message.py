from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from injector import inject

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

    def __call__(self, request: SendExtMessageRequest) -> SendExtMessageResponse:
        message = self.external_message_repository.get_by_id(request.message_id)
        if message is None:
            rejection_reason = SendExtMessageResponse.RejectionReason.message_not_found
            return SendExtMessageResponse(rejection_reason=rejection_reason)
        sent_message_id = self.external_message_repository.send_message(message.id)
        if sent_message_id is None:
            rejection_reason = (
                SendExtMessageResponse.RejectionReason.message_could_not_be_sent
            )
            return SendExtMessageResponse(rejection_reason=rejection_reason)
        return SendExtMessageResponse(rejection_reason=None)
