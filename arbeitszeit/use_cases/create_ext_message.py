from dataclasses import dataclass
from enum import Enum
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import ExternalMessageRepository


@dataclass
class CreateExtMessageRequest:
    sender_adress: str
    receiver_adress: str
    title: str
    content_html: str


@dataclass
class CreateExtMessageResponse:
    class RejectionReason(Exception, Enum):
        ...

    rejection_reason: Optional[RejectionReason]
    message_id: UUID

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@inject
@dataclass
class CreateExtMessage:
    external_message_repository: ExternalMessageRepository

    def __call__(self, request: CreateExtMessageRequest) -> CreateExtMessageResponse:
        message = self.external_message_repository.create_message(
            sender_adress=request.sender_adress,
            receiver_adress=request.receiver_adress,
            title=request.title,
            content_html=request.content_html,
        )
        return CreateExtMessageResponse(rejection_reason=None, message_id=message.id)
