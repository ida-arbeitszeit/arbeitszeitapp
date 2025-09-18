from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway


@dataclass
class AnswerCompanyWorkInviteRequest:
    is_accepted: bool
    invite_id: UUID
    user: UUID


@dataclass
class AnswerCompanyWorkInviteResponse:
    class Failure(Exception, Enum):
        invite_not_found = auto()
        member_was_not_invited = auto()

    is_success: bool
    is_accepted: bool
    company_name: Optional[str]
    failure_reason: Optional[Failure]


@dataclass
class AnswerCompanyWorkInviteUseCase:
    database_gateway: DatabaseGateway

    def execute(
        self, request: AnswerCompanyWorkInviteRequest
    ) -> AnswerCompanyWorkInviteResponse:
        invite = (
            self.database_gateway.get_company_work_invites()
            .with_id(request.invite_id)
            .first()
        )
        if invite is None:
            return self._create_failure_response(
                reason=AnswerCompanyWorkInviteResponse.Failure.invite_not_found
            )
        if invite.member != request.user:
            return self._create_failure_response(
                reason=AnswerCompanyWorkInviteResponse.Failure.member_was_not_invited
            )
        elif request.is_accepted:
            self.database_gateway.get_companies().with_id(invite.company).add_worker(
                invite.member
            )
            self.database_gateway.get_company_work_invites().with_id(
                request.invite_id
            ).delete()
        elif not request.is_accepted:
            self.database_gateway.get_company_work_invites().with_id(
                request.invite_id
            ).delete()
        company = self.database_gateway.get_companies().with_id(invite.company).first()
        assert company
        return AnswerCompanyWorkInviteResponse(
            is_success=True,
            is_accepted=request.is_accepted,
            company_name=company.name,
            failure_reason=None,
        )

    def _create_failure_response(
        self, reason: AnswerCompanyWorkInviteResponse.Failure
    ) -> AnswerCompanyWorkInviteResponse:
        return AnswerCompanyWorkInviteResponse(
            is_success=False,
            is_accepted=False,
            company_name=None,
            failure_reason=reason,
        )
