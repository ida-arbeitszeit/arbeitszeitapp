from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import (
    CompanyRepository,
    MemberRepository,
    MessageRepository,
    WorkerInviteRepository,
)
from arbeitszeit.user_action import UserAction, UserActionType


@inject
@dataclass
class InviteWorkerToCompanyUseCase:
    @dataclass
    class Request:
        company: UUID
        worker: UUID

    @dataclass
    class Response:
        is_success: bool
        invite_id: Optional[UUID] = None

    worker_invite_repository: WorkerInviteRepository
    member_repository: MemberRepository
    company_repository: CompanyRepository
    message_repository: MessageRepository

    def __call__(self, request: Request) -> Response:
        addressee = self.member_repository.get_by_id(request.worker)
        if addressee is None:
            return self.Response(is_success=False)
        sender = self.company_repository.get_by_id(request.company)
        if sender is None:
            return self.Response(is_success=False)
        if self.worker_invite_repository.is_worker_invited_to_company(
            request.company, request.worker
        ):
            return self.Response(is_success=False)
        else:
            invite_id = self.worker_invite_repository.create_company_worker_invite(
                request.company, request.worker
            )
            self.message_repository.create_message(
                sender=sender,
                addressee=addressee,
                title=f"Company {sender.name} invited you to join them",
                content="",
                sender_remarks=None,
                reference=UserAction(
                    type=UserActionType.answer_invite,
                    reference=invite_id,
                ),
            )
            return self.Response(is_success=True, invite_id=invite_id)
