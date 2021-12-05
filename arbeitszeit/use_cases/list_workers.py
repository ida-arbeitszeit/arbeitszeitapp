from dataclasses import dataclass
from typing import List
from uuid import UUID

from injector import inject

from arbeitszeit.entities import Member
from arbeitszeit.repositories import CompanyRepository, CompanyWorkerRepository


@dataclass
class ListWorkersResponse:
    workers: List[Member]


@inject
@dataclass
class ListWorkers:
    company_repository: CompanyRepository
    company_worker_repository: CompanyWorkerRepository

    def __call__(self, company_id: UUID) -> ListWorkersResponse:
        company = self.company_repository.get_by_id(company_id)
        if company is None:
            return ListWorkersResponse(workers=[])
        workers = self.company_worker_repository.get_company_workers(company)
        return ListWorkersResponse(workers=[worker for worker in workers])
