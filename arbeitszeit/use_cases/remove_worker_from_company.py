from dataclasses import dataclass
from enum import Enum, auto
from uuid import UUID

from arbeitszeit.email_notifications import EmailSender, WorkerRemovalNotification
from arbeitszeit.records import Company, Member
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
class RemoveWorkerFromCompanyUseCase:
    database_gateway: DatabaseGateway
    email_sender: EmailSender

    def remove_worker_from_company(self, request: Request) -> Response:
        workplace_record = self.database_gateway.get_companies().with_id(
            request.company
        )
        if not workplace_record:
            return Response(Response.RejectionReason.company_not_found)
        worker = self.database_gateway.get_members().with_id(request.worker).first()
        if not worker:
            return Response(Response.RejectionReason.worker_not_found)
        workplace_record = workplace_record.that_are_workplace_of_member(worker.id)
        workplace = workplace_record.first()
        if not workplace:
            return Response(Response.RejectionReason.not_workplace_of_worker)
        workplace_record.remove_worker(worker.id)
        self._notify_worker_and_company(worker, workplace)
        return Response(None)

    def _notify_worker_and_company(self, worker: Member, workplace: Company) -> None:
        worker_record = (
            self.database_gateway.get_members()
            .with_id(worker.id)
            .joined_with_email_address()
            .first()
        )
        company_record = (
            self.database_gateway.get_companies()
            .with_id(workplace.id)
            .joined_with_email_address()
            .first()
        )
        if worker_record and company_record is not None:
            _, worker_email = worker_record
            _, company_email = company_record
            self.email_sender.send_email(
                WorkerRemovalNotification(
                    worker_email=worker_email.address,
                    worker_name=worker.get_name(),
                    worker_id=str(worker.id),
                    company_email=company_email.address,
                    company_name=workplace.name,
                )
            )
