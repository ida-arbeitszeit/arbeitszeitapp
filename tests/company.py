from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.repositories import (
    CompanyRepository,
    CompanyWorkerRepository,
    MemberRepository,
)


@dataclass
class CompanyManager:
    worker_repository: CompanyWorkerRepository
    company_repository: CompanyRepository
    member_repository: MemberRepository

    def add_worker_to_company(self, company: UUID, worker: UUID) -> None:
        company_entity = self.company_repository.get_by_id(company)
        assert company_entity
        member_entity = self.member_repository.get_by_id(worker)
        assert member_entity
        self.worker_repository.add_worker_to_company(
            company_entity,
            member_entity,
        )
