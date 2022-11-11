from uuid import uuid4

from arbeitszeit_flask.database.repositories import CompanyWorkerRepository
from tests.data_generators import CompanyGenerator, MemberGenerator

from .flask import FlaskTestCase


class RepositoryTester(FlaskTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.member_generator: MemberGenerator = self.injector.get(MemberGenerator)
        self.repo: CompanyWorkerRepository = self.injector.get(CompanyWorkerRepository)
        self.company_generator: CompanyGenerator = self.injector.get(CompanyGenerator)

    def test_that_no_workplaces_are_returned_for_new_member_account(self) -> None:
        member = self.member_generator.create_member()
        workplaces = self.repo.get_member_workplaces(member)
        assert not workplaces

    def test_that_no_workplaces_are_returned_non_existing_worker(self) -> None:
        workplaces = self.repo.get_member_workplaces(uuid4())
        assert not workplaces

    def test_that_workplace_is_returned_after_one_is_registered(self) -> None:
        member = self.member_generator.create_member()
        company = self.company_generator.create_company_entity()
        self.repo.add_worker_to_company(company=company.id, worker=member)
        assert [company] == self.repo.get_member_workplaces(member)

    def test_no_company_workers_are_returned_for_fresh_company(self) -> None:
        company = self.company_generator.create_company_entity()
        assert not self.repo.get_company_workers(company.id)

    def test_worker_that_was_added_shows_up_in_company_workers(self) -> None:
        company = self.company_generator.create_company_entity()
        member = self.member_generator.create_member()
        self.repo.add_worker_to_company(company=company.id, worker=member)
        assert member in [
            woker.id for woker in self.repo.get_company_workers(company.id)
        ]
