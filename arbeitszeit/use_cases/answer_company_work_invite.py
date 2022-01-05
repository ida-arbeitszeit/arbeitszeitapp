from dataclasses import dataclass
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import (
    CompanyWorkerRepository,
    MemberRepository,
    WorkerInviteRepository,
)


@dataclass
class AnswerCompanyWorkInviteRequest:
    is_accepted: bool
    invite_id: UUID
    user: UUID


@dataclass
class AnswerCompanyWorkInviteResponse:
    is_success: bool
    is_accepted: bool


@inject
@dataclass
class AnswerCompanyWorkInvite:
    worker_invite_repository: WorkerInviteRepository
    company_worker_repository: CompanyWorkerRepository
    member_repository: MemberRepository

    def __call__(
        self, request: AnswerCompanyWorkInviteRequest
    ) -> AnswerCompanyWorkInviteResponse:
        invite = self.worker_invite_repository.get_by_id(request.invite_id)
        if invite is None:
            return self._create_failure_response()
        if invite.member.id != request.user:
            return self._create_failure_response()
        elif request.is_accepted:
            self.company_worker_repository.add_worker_to_company(
                invite.company,
                invite.member,
            )
        self.worker_invite_repository.delete_invite(request.invite_id)
        return AnswerCompanyWorkInviteResponse(
            is_success=True, is_accepted=request.is_accepted
        )

    def _create_failure_response(self) -> AnswerCompanyWorkInviteResponse:
        return AnswerCompanyWorkInviteResponse(is_success=False, is_accepted=False)
