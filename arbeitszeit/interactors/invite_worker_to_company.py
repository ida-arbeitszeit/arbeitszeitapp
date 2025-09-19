from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from uuid import UUID

from arbeitszeit.email_notifications import EmailSender, WorkerInvitation
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class InviteWorkerToCompanyInteractor:
    @dataclass
    class Request:
        company: UUID
        worker: UUID

    @dataclass
    class Response:
        class RejectionReason(Enum):
            WORKER_NOT_FOUND = auto()
            COMPANY_NOT_FOUND = auto()
            WORKER_ALREADY_WORKS_FOR_COMPANY = auto()
            INVITATION_ALREADY_ISSUED = auto()

        worker: UUID
        invite_id: UUID | None = None
        rejection_reason: RejectionReason | None = None

    database_gateway: DatabaseGateway
    email_sender: EmailSender

    def invite_worker(self, request: Request) -> Response:
        addressee = self.database_gateway.get_members().with_id(request.worker).first()
        if addressee is None:
            return self.Response(
                worker=request.worker,
                rejection_reason=self.Response.RejectionReason.WORKER_NOT_FOUND,
            )
        if not self.database_gateway.get_companies().with_id(request.company):
            return self.Response(
                worker=request.worker,
                rejection_reason=self.Response.RejectionReason.COMPANY_NOT_FOUND,
            )
        if (
            self.database_gateway.get_members()
            .with_id(request.worker)
            .working_at_company(request.company)
        ):
            return self.Response(
                worker=request.worker,
                rejection_reason=self.Response.RejectionReason.WORKER_ALREADY_WORKS_FOR_COMPANY,
            )
        if (
            self.database_gateway.get_company_work_invites()
            .addressing(request.worker)
            .issued_by(request.company)
        ):
            return self.Response(
                worker=request.worker,
                rejection_reason=self.Response.RejectionReason.INVITATION_ALREADY_ISSUED,
            )
        else:
            invite = self.database_gateway.create_company_work_invite(
                request.company, request.worker
            )
            self.notify_member_about_invitation(member=invite.member, invite=invite.id)
            return self.Response(worker=request.worker, invite_id=invite.id)

    def notify_member_about_invitation(self, member: UUID, invite: UUID) -> None:
        record = (
            self.database_gateway.get_members()
            .with_id(member)
            .joined_with_email_address()
            .first()
        )
        if record is not None:
            _, member_email = record
            self.email_sender.send_email(
                WorkerInvitation(worker_email=member_email.address, invite=invite)
            )
