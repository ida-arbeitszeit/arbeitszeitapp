from dataclasses import dataclass
from uuid import UUID

from arbeitszeit.repositories import DatabaseGateway


@dataclass
class CompanyManager:
    database: DatabaseGateway

    def add_worker_to_company(self, company: UUID, worker: UUID) -> None:
        companies = self.database.get_companies().with_id(company)
        assert companies
        assert self.database.get_members().with_id(worker)
        companies.add_worker(worker)
