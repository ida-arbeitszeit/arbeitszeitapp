from dataclasses import dataclass
from typing import List

from injector import inject

from arbeitszeit.entities import Member
from arbeitszeit.repositories import CompanyWorkerRepository


@dataclass
class WorkplacesResponse:
    workplace_name: str
    workplace_email: str


@inject
@dataclass
class GetMemberWorkplaces:
    company_worker_repository: CompanyWorkerRepository

    def __call__(self, member: Member) -> List[WorkplacesResponse]:
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
