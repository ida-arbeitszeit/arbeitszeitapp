from dataclasses import dataclass
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import (
    CompanyRepository,
    MemberRepository,
    WorkerInviteRepository,
)


@dataclass
class InviteWorkerToCompanyRequest:
    company: UUID
    worker: UUID


@dataclass
class InviteWorkerToCompanyResponse:
    is_success: bool


@inject
@dataclass
class InviteWorkerToCompany:
    worker_invite_repository: WorkerInviteRepository
    member_repository: MemberRepository
    company_repository: CompanyRepository

    def __call__(
        self, request: InviteWorkerToCompanyRequest
    ) -> InviteWorkerToCompanyResponse:
        if self.member_repository.get_by_id(request.worker) is None:
            return InviteWorkerToCompanyResponse(is_success=False)
        if self.company_repository.get_by_id(request.company) is None:
            return InviteWorkerToCompanyResponse(is_success=False)
        if self.worker_invite_repository.is_worker_invited_to_company(
            request.company, request.worker
        ):
            return InviteWorkerToCompanyResponse(is_success=False)
        else:
            self.worker_invite_repository.create_company_worker_invite(
                request.company, request.worker
            )
            return InviteWorkerToCompanyResponse(is_success=True)
