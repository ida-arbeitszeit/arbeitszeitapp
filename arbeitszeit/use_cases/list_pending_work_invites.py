from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway


@dataclass
class Request:
    company: UUID


@dataclass
class PendingInvite:
    member_id: UUID
    member_name: str


@dataclass
class Response:
    pending_invites: list[PendingInvite]


@dataclass
class ListPendingWorkInvitesUseCase:
    database_gateway: DatabaseGateway

    def list_pending_work_invites(self, request: Request) -> Response:
        pending_invites = (
            self.database_gateway.get_company_work_invites()
            .issued_by(request.company)
            .joined_with_member()
        )
        if not pending_invites:
            return Response(pending_invites=[])
        return Response(
            pending_invites=[
                PendingInvite(
                    member_id=member.id,
                    member_name=member.name,
                )
                for _, member in pending_invites
            ]
        )
