from dataclasses import dataclass
from typing import List
from uuid import UUID

from arbeitszeit.records import EmailAddress, Member
from arbeitszeit.repositories import DatabaseGateway


@dataclass
class ListedWorker:
    id: UUID
    name: str
    email: str


@dataclass
class Response:
    workers: List[ListedWorker]


@dataclass
class Request:
    company: UUID


@dataclass
class ListWorkersInteractor:
    database: DatabaseGateway

    def execute(self, request: Request) -> Response:
        if not self.database.get_companies().with_id(request.company):
            return Response(workers=[])
        members = self.database.get_members().working_at_company(request.company)
        return Response(
            workers=[
                self._create_worker_response_model(member, mail)
                for member, mail in members.joined_with_email_address()
            ]
        )

    def _create_worker_response_model(
        self, member: Member, email: EmailAddress
    ) -> ListedWorker:
        return ListedWorker(
            id=member.id,
            name=member.name,
            email=email.address,
        )
