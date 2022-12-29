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
        assert self.company_repository.get_all_companies().with_id(company).first()
        assert self.member_repository.get_members().with_id(worker)
        self.worker_repository.add_worker_to_company(
            company,
            worker,
        )
