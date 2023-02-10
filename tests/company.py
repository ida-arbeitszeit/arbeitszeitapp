from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.repositories import CompanyRepository, MemberRepository


@dataclass
class CompanyManager:
    company_repository: CompanyRepository
    member_repository: MemberRepository

    def add_worker_to_company(self, company: UUID, worker: UUID) -> None:
        companies = self.company_repository.get_companies().with_id(company)
        assert companies
        assert self.member_repository.get_members().with_id(worker)
        companies.add_worker(worker)
