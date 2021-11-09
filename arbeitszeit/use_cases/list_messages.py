from dataclasses import dataclass
from typing import List
from uuid import UUID

from injector import inject

from arbeitszeit.entities import Message
from arbeitszeit.repositories import (
    CompanyRepository,
    MemberRepository,
    MessageRepository,
)


@dataclass
class ListMessagesRequest:
    user: UUID


@dataclass
class ListedMessage:
    title: str
    sender_name: str
    message_id: UUID
    is_read: bool


@dataclass
class ListMessagesResponse:
    messages: List[ListedMessage]


@inject
@dataclass
class ListMessages:
    member_repository: MemberRepository
    company_repository: CompanyRepository
    message_repository: MessageRepository

    def __call__(self, request: ListMessagesRequest) -> ListMessagesResponse:
        if not self._exists_requesting_user(request.user):
            return ListMessagesResponse(messages=[])
        messages = self.message_repository.get_messages_to_user(request.user)
        return ListMessagesResponse(
            messages=[
                self._create_message_response_model(message) for message in messages
            ]
        )

    def _exists_requesting_user(self, id: UUID) -> bool:
        if self.member_repository.get_by_id(id):
            return True
        return bool(self.company_repository.get_by_id(id))

    def _create_message_response_model(self, message: Message) -> ListedMessage:
        return ListedMessage(
            title=message.title,
            sender_name=message.sender.get_name(),
            message_id=message.id,
            is_read=message.is_read,
        )
