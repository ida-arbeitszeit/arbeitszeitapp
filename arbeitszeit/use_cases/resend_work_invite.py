from dataclasses import dataclass
from enum import Enum, auto
from uuid import UUID

from arbeitszeit.email_notifications import EmailSender, WorkerInvitation
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class Request:
    company: UUID
    worker: UUID


@dataclass
class Response:
    class RejectionReason(Enum):
        INVITE_DOES_NOT_EXIST = auto()

    rejection_reason: RejectionReason | None = None


@dataclass
class ResendWorkInviteUseCase:
    database_gateway: DatabaseGateway
    email_sender: EmailSender

    def resend_work_invite(self, request: Request) -> Response:
        invite = (
            self.database_gateway.get_company_work_invites()
            .issued_by(request.company)
            .addressing(request.worker)
            .first()
        )
        if not invite:
            return Response(
                rejection_reason=Response.RejectionReason.INVITE_DOES_NOT_EXIST
            )
        self.notify_member_about_invitation(member=invite.member, invite=invite.id)
        return Response()

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
