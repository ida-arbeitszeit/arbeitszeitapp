from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import MemberRepository, WorkerInviteMessageRepository


@inject
@dataclass
class CheckForUnreadMessages:
    @dataclass
    class Request:
        user: UUID

    @dataclass
    class Response:
        has_unread_messages: bool

    member_repository: MemberRepository
    worker_invite_message_repository: WorkerInviteMessageRepository

    def __call__(self, request: Request) -> Response:
        if self.member_repository.get_by_id(request.user) is None:
            return self.Response(has_unread_messages=False)
        else:
            has_unread_messages = (
                self.worker_invite_message_repository.has_unread_messages_for_user(
                    request.user
                )
            )
            return self.Response(has_unread_messages=has_unread_messages)
