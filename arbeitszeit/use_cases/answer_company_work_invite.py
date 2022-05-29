from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.entities import WorkerInviteMessage
from arbeitszeit.repositories import (
    CompanyWorkerRepository,
    WorkerInviteMessageRepository,
    WorkerInviteRepository,
)


@inject
@dataclass
class AnswerCompanyWorkInvite:
    @dataclass
    class Request:
        is_accepted: bool
        invite_id: UUID
        user: UUID

    @dataclass
    class Response:
        class Failure(Exception, Enum):
            invite_not_found = auto()
            member_was_not_invited = auto()
            message_not_found = auto()

        is_success: bool
        is_accepted: bool
        company_name: Optional[str]
        failure_reason: Optional[Failure]

    worker_invite_repository: WorkerInviteRepository
    company_worker_repository: CompanyWorkerRepository
    worker_invite_message_repository: WorkerInviteMessageRepository

    def __call__(self, request: Request) -> Response:
        invite = self.worker_invite_repository.get_by_id(request.invite_id)
        if invite is None:
            return self._create_failure_response(
                reason=self.Response.Failure.invite_not_found
            )
        if invite.member.id != request.user:
            return self._create_failure_response(
                reason=self.Response.Failure.member_was_not_invited
            )
        elif request.is_accepted:
            self.company_worker_repository.add_worker_to_company(
                invite.company,
                invite.member,
            )
        message = self._get_invite_message(request)
        if message is None:
            return self._create_failure_response(
                reason=self.Response.Failure.message_not_found
            )
        self.worker_invite_message_repository.delete_message(message.id)
        self.worker_invite_repository.delete_invite(request.invite_id)
        return self.Response(
            is_success=True,
            is_accepted=request.is_accepted,
            company_name=invite.company.name,
            failure_reason=None,
        )

    def _create_failure_response(self, reason: Response.Failure) -> Response:
        return self.Response(
            is_success=False,
            is_accepted=False,
            company_name=None,
            failure_reason=reason,
        )

    def _get_invite_message(self, request: Request) -> Optional[WorkerInviteMessage]:
        return self.worker_invite_message_repository.get_by_invite(request.invite_id)
