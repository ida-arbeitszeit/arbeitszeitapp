from dataclasses import dataclass
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import MemberRepository


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

    def __call__(
        self, request: CheckForUnreadMessagesRequest
    ) -> CheckForUnreadMessagesResponse:
        if self.member_repository.get_by_id(request.user) is None:
            return CheckForUnreadMessagesResponse(has_unread_messages=False)
        else:
            return CheckForUnreadMessagesResponse(has_unread_messages=True)
