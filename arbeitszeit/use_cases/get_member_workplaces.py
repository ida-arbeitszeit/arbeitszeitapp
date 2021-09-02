from dataclasses import dataclass
from typing import List
from uuid import UUID

from injector import inject

from arbeitszeit.repositories import CompanyWorkerRepository


@dataclass
class WorkplacesResponse:
    workplace_name: str
    workplace_email: str


@inject
@dataclass
class GetMemberWorkplaces:
    company_worker_repository: CompanyWorkerRepository

    def __call__(self, member: UUID) -> List[WorkplacesResponse]:
        workplaces = [
            WorkplacesResponse(
                workplace_name=workplace.name,
                workplace_email=workplace.email,
            )
            for workplace in self.company_worker_repository.get_member_workplaces(
                member
            )
        ]
        return workplaces
