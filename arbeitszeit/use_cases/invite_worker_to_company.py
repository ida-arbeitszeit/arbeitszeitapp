from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import (
    CompanyRepository,
    MemberRepository,
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

    def __call__(self, request: Request) -> Response:
        addressee = self.member_repository.get_members().with_id(request.worker).first()
        if addressee is None:
            return self.Response(is_success=False)
        if not self.company_repository.get_companies().with_id(request.company):
            return self.Response(is_success=False)
        if self.worker_invite_repository.is_worker_invited_to_company(
            request.company, request.worker
        ):
            return self.Response(is_success=False)
        else:
            invite_id = self.worker_invite_repository.create_company_worker_invite(
                request.company, request.worker
            )
            return self.Response(is_success=True, invite_id=invite_id)
