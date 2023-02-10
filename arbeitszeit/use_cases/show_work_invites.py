from dataclasses import dataclass
from typing import List
from uuid import UUID

from arbeitszeit.repositories import WorkerInviteRepository


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
    worker_invite_repository: WorkerInviteRepository

    def __call__(self, request: ShowWorkInvitesRequest) -> ShowWorkInvitesResponse:
        return ShowWorkInvitesResponse(
            invites=[
                WorkInvitation(
                    company_id=company_id,
                )
                for company_id in self.worker_invite_repository.get_companies_worker_is_invited_to(
                    request.member
                )
            ]
        )
