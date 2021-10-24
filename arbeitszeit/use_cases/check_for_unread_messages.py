from dataclasses import dataclass
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import MemberRepository, MessageRepository


@dataclass
class CheckForUnreadMessagesRequest:
    user: UUID


@dataclass
class CheckForUnreadMessagesResponse:
    has_unread_messages: bool


@inject
@dataclass
class CheckForUnreadMessages:
    member_repository: MemberRepository
    message_repository: MessageRepository

    def __call__(
        self, request: CheckForUnreadMessagesRequest
    ) -> CheckForUnreadMessagesResponse:
        if self.member_repository.get_by_id(request.user) is None:
            return CheckForUnreadMessagesResponse(has_unread_messages=False)
        else:
            has_unread_messages = self.message_repository.has_unread_messages_for_user(
                request.user
            )
            return CheckForUnreadMessagesResponse(
                has_unread_messages=has_unread_messages
            )
