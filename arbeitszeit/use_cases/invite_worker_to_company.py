from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from arbeitszeit.member_notifications import MemberNotifier
from arbeitszeit.repositories import DatabaseGateway


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
    member_notifier: MemberNotifier

    def __call__(self, request: Request) -> Response:
        addressee = self.database_gateway.get_members().with_id(request.worker).first()
        if addressee is None:
            return self.Response(is_success=False)
        if not self.database_gateway.get_companies().with_id(request.company):
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
            self.member_notifier.notify_member_about_invitation(
                member=invite.member, invite=invite.id
            )
            return self.Response(is_success=True, invite_id=invite.id)
