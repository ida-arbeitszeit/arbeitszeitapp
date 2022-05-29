from __future__ import annotations

from dataclasses import dataclass
from typing import Union
from uuid import UUID

from injector import inject

from arbeitszeit.entities import WorkerInviteMessage
from arbeitszeit.repositories import MemberRepository, WorkerInviteMessageRepository


@inject
@dataclass
class ReadWorkerInviteMessage:
    @dataclass
    class Failure(Exception):
        pass

    @dataclass
    class Success:
        invite_id: UUID

    @dataclass
    class Request:
        reader_id: UUID
        message_id: UUID

    Response = Union["Failure", "Success"]

    member_repository: MemberRepository
    worker_invite_message_repository: WorkerInviteMessageRepository

    def __call__(self, request: Request) -> Response:
        try:
            message = self._validate_request(request)
        except self.Failure as failure:
            return failure
        self.worker_invite_message_repository.mark_as_read(message)
        return self.Success(invite_id=message.invite_id)

    def _validate_request(self, request: Request) -> WorkerInviteMessage:
        reader = self.member_repository.get_by_id(request.reader_id)
        if reader is None:
            raise self.Failure()
        message = self.worker_invite_message_repository.get_by_id(request.message_id)
        if message is None:
            raise self.Failure()
        if message.worker != reader:
            raise self.Failure()
        return message
