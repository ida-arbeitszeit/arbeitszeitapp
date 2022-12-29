from dataclasses import dataclass
from typing import List
from uuid import UUID

from injector import inject

from arbeitszeit.entities import Member
from arbeitszeit.repositories import CompanyRepository, MemberRepository


@dataclass
class ListedWorker:
    id: UUID
    name: str
    email: str


@dataclass
class ListWorkersResponse:
    workers: List[ListedWorker]


@dataclass
class ListWorkersRequest:
    company: UUID


@inject
@dataclass
class ListWorkers:
    company_repository: CompanyRepository
    member_repository: MemberRepository

    def __call__(self, request: ListWorkersRequest) -> ListWorkersResponse:
        if not self.company_repository.get_companies().with_id(request.company):
            return ListWorkersResponse(workers=[])
        members = self.member_repository.get_members().working_at_company(
            request.company
        )
        return ListWorkersResponse(
            workers=[self._create_worker_response_model(member) for member in members]
        )

    def _create_worker_response_model(self, member: Member) -> ListedWorker:
        return ListedWorker(
            id=member.id,
            name=member.name,
            email=member.email,
        )
