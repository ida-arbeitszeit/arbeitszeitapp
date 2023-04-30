from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from arbeitszeit.repositories import (
    CompanyRepository,
    DatabaseGateway,
    MemberRepository,
)


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

    database_gateway: DatabaseGateway
    member_repository: MemberRepository
    company_repository: CompanyRepository

    def __call__(self, request: Request) -> Response:
        addressee = self.member_repository.get_members().with_id(request.worker).first()
        if addressee is None:
            return self.Response(is_success=False)
        if not self.company_repository.get_companies().with_id(request.company):
            return self.Response(is_success=False)
        if (
            self.database_gateway.get_company_work_invites()
            .addressing(request.worker)
            .issued_by(request.company)
        ):
            return self.Response(is_success=False)
        else:
            invite = self.database_gateway.create_company_work_invite(
                request.company, request.worker
            )
            return self.Response(is_success=True, invite_id=invite.id)
