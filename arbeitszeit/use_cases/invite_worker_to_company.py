from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.repositories import (
    CompanyRepository,
    MemberRepository,
    WorkerInviteMessageRepository,
    WorkerInviteRepository,
)


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
    worker_invite_message_repository: WorkerInviteMessageRepository
    datetime_service: DatetimeService

    def __call__(self, request: Request) -> Response:
        worker = self.member_repository.get_by_id(request.worker)
        if worker is None:
            return self.Response(is_success=False)
        company = self.company_repository.get_by_id(request.company)
        if company is None:
            return self.Response(is_success=False)
        if self.worker_invite_repository.is_worker_invited_to_company(
            request.company, request.worker
        ):
            return self.Response(is_success=False)
        else:
            invite_id = self.worker_invite_repository.create_company_worker_invite(
                request.company, request.worker
            )
            self.worker_invite_message_repository.create_message(
                invite_id=invite_id,
                company=company,
                worker=worker,
                creation_date=self.datetime_service.now(),
            )
            return self.Response(is_success=True, invite_id=invite_id)
