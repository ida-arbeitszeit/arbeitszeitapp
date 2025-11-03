from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway


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


@dataclass
class ShowCompanyWorkInviteDetailsInteractor:
    database_gateway: DatabaseGateway

    def show_company_work_invite_details(
        self, request: ShowCompanyWorkInviteDetailsRequest
    ) -> ShowCompanyWorkInviteDetailsResponse:
        if not self.database_gateway.get_members().with_id(request.member):
            return failure_response
        invite = (
            self.database_gateway.get_company_work_invites()
            .with_id(request.invite)
            .first()
        )
        if invite is None:
            return failure_response
        if invite.member != request.member:
            return failure_response
        company = self.database_gateway.get_companies().with_id(invite.company).first()
        assert company
        return ShowCompanyWorkInviteDetailsResponse(
            details=ShowCompanyWorkInviteDetailsResponse.Details(
                company_name=company.name,
                invite_id=request.invite,
            ),
        )


failure_response = ShowCompanyWorkInviteDetailsResponse(details=None)
