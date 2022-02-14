from injector import Module, provider

from arbeitszeit.repositories import (
    CompanyRepository,
    CompanyWorkerRepository,
    MemberRepository,
)
from tests.company import CompanyManager


class TestingModule(Module):
    @provider
    def provide_company_manager(
        self,
        company_repository: CompanyRepository,
        member_repository: MemberRepository,
        company_worker_repository: CompanyWorkerRepository,
    ) -> CompanyManager:
        return CompanyManager(
            worker_repository=company_worker_repository,
            company_repository=company_repository,
            member_repository=member_repository,
        )
