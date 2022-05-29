from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List
from uuid import UUID

from injector import inject

from arbeitszeit.entities import WorkerInviteMessage
from arbeitszeit.repositories import (
    CompanyRepository,
    MemberRepository,
    WorkerInviteMessageRepository,
)


@inject
@dataclass
class ListMessages:
    @dataclass
    class Request:
        user: UUID

    @dataclass
    class InviteMessage:
        message_id: UUID
        company_name: str
        is_read: bool
        creation_date: datetime

    @dataclass
    class Response:
        worker_invite_messages: List[ListMessages.InviteMessage]

    member_repository: MemberRepository
    company_repository: CompanyRepository
    worker_invite_message_repository: WorkerInviteMessageRepository

    def __call__(self, request: Request) -> Response:
        if not self._exists_requesting_user(request.user):
            return self.Response(worker_invite_messages=[])
        worker_invite_messages = (
            self.worker_invite_message_repository.get_messages_to_user(request.user)
        )
        return self.Response(
            worker_invite_messages=[
                self._create_message_response_model(message)
                for message in worker_invite_messages
            ]
        )

    def _exists_requesting_user(self, id: UUID) -> bool:
        if self.member_repository.get_by_id(id):
            return True
        return bool(self.company_repository.get_by_id(id))

    def _create_message_response_model(
        self, message: WorkerInviteMessage
    ) -> InviteMessage:
        return self.InviteMessage(
            message_id=message.id,
            company_name=message.company.name,
            is_read=message.is_read,
            creation_date=message.creation_date,
        )
