from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import MemberRepository, WorkerInviteRepository


@dataclass
class ShowCompanyWorkInviteDetailsResponse:
    @dataclass
    class Details:
        company_name: str
        invite_id: UUID

    details: Optional[Details]

    @property
    def is_success(self) -> bool:
        return self.details is not None


@dataclass
class ShowCompanyWorkInviteDetailsRequest:
    invite: UUID
    member: UUID


@inject
@dataclass
class ShowCompanyWorkInviteDetailsUseCase:
    member_repository: MemberRepository
    worker_invite_repository: WorkerInviteRepository

    def show_company_work_invite_details(
        self, request: ShowCompanyWorkInviteDetailsRequest
    ) -> ShowCompanyWorkInviteDetailsResponse:
        if not self.member_repository.get_members().with_id(request.member):
            return failure_response
        invite = self.worker_invite_repository.get_by_id(request.invite)
        if invite is None:
            return failure_response
        if invite.member.id != request.member:
            return failure_response
        return ShowCompanyWorkInviteDetailsResponse(
            details=ShowCompanyWorkInviteDetailsResponse.Details(
                company_name=invite.company.name,
                invite_id=request.invite,
            ),
        )


failure_response = ShowCompanyWorkInviteDetailsResponse(details=None)
