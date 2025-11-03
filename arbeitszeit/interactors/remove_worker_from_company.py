from dataclasses import dataclass
from enum import Enum, auto
from uuid import UUID

from arbeitszeit.email_notifications import EmailSender, WorkerRemovalNotification
from arbeitszeit.records import Company, EmailAddress, Member
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class Request:
    worker: UUID
    company: UUID


@dataclass
class Response:
    class RejectionReason(Enum):
        company_not_found = auto()
        not_workplace_of_worker = auto()
        worker_not_found = auto()

    rejection_reason: RejectionReason | None

    @property
    def is_rejected(self) -> bool:
        return self.rejection_reason is not None


@dataclass
class RemoveWorkerFromCompanyInteractor:
    database_gateway: DatabaseGateway
    email_sender: EmailSender

    def remove_worker_from_company(self, request: Request) -> Response:
        company_record = self.database_gateway.get_companies().with_id(request.company)
        if not company_record:
            return Response(Response.RejectionReason.company_not_found)
        company_and_email = company_record.joined_with_email_address().first()
        assert company_and_email
        worker_and_email = (
            self.database_gateway.get_members()
            .with_id(request.worker)
            .joined_with_email_address()
            .first()
        )
        if not worker_and_email:
            return Response(Response.RejectionReason.worker_not_found)
        workplace = company_record.that_are_workplace_of_member(worker_and_email[0].id)
        if not workplace:
            return Response(Response.RejectionReason.not_workplace_of_worker)
        workplace.remove_worker(worker_and_email[0].id)
        self._notify_worker_and_company(
            worker=worker_and_email[0],
            worker_email=worker_and_email[1],
            workplace=company_and_email[0],
            company_email=company_and_email[1],
        )
        return Response(None)

    def _notify_worker_and_company(
        self,
        worker: Member,
        worker_email: EmailAddress,
        workplace: Company,
        company_email: EmailAddress,
    ) -> None:
        self.email_sender.send_email(
            WorkerRemovalNotification(
                worker_email=worker_email.address,
                worker_name=worker.get_name(),
                worker_id=worker.id,
                company_email=company_email.address,
                company_name=workplace.name,
            )
        )
