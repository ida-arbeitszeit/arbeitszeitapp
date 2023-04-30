from dataclasses import dataclass
from typing import List
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway


@dataclass
class WorkInvitation:
    company_id: UUID


@dataclass
class ShowWorkInvitesResponse:
    invites: List[WorkInvitation]


@dataclass
class ShowWorkInvitesRequest:
    member: UUID


@dataclass
class ShowWorkInvites:
    database_gateway: DatabaseGateway

    def __call__(self, request: ShowWorkInvitesRequest) -> ShowWorkInvitesResponse:
        return ShowWorkInvitesResponse(
            invites=[
                WorkInvitation(
                    company_id=invite.company,
                )
                for invite in self.database_gateway.get_company_work_invites().addressing(
                    request.member
                )
            ]
        )
