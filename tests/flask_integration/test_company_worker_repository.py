from arbeitszeit_flask.database.repositories import (
    CompanyRepository,
    CompanyWorkerRepository,
)
from tests.data_generators import CompanyGenerator, MemberGenerator

from .flask import FlaskTestCase


class RepositoryTester(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.member_generator: MemberGenerator = self.injector.get(MemberGenerator)
        self.repo: CompanyWorkerRepository = self.injector.get(CompanyWorkerRepository)
        self.company_generator: CompanyGenerator = self.injector.get(CompanyGenerator)
        self.company_repository = self.injector.get(CompanyRepository)

    def test_that_workplace_is_returned_after_one_is_registered(self) -> None:
        member = self.member_generator.create_member()
        company = self.company_generator.create_company_entity()
        self.repo.add_worker_to_company(company=company.id, worker=member)
        assert (
            company
            in self.company_repository.get_companies().that_are_workplace_of_member(
                member
            )
        )
