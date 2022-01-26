from uuid import uuid4

from arbeitszeit_flask.database.repositories import (
    CompanyWorkerRepository,
    MemberRepository,
)
from tests.data_generators import CompanyGenerator, MemberGenerator
from tests.flask_integration.dependency_injection import injection_test


@injection_test
def test_that_no_workplaces_are_returned_for_new_member_account(
    member_generator: MemberGenerator,
    repo: CompanyWorkerRepository,
):
    member = member_generator.create_member()
    workplaces = repo.get_member_workplaces(member.id)
    assert not workplaces


@injection_test
def test_that_no_workplaces_are_returned_non_existing_worker(
    repo: CompanyWorkerRepository,
):
    workplaces = repo.get_member_workplaces(uuid4())
    assert not workplaces


@injection_test
def test_that_workplace_is_returned_after_one_is_registered(
    member_generator: MemberGenerator,
    member_repository: MemberRepository,
    company_generator: CompanyGenerator,
    repo: CompanyWorkerRepository,
):
    member = member_generator.create_member()
    company = company_generator.create_company()
    repo.add_worker_to_company(company=company, worker=member)
    assert [company] == repo.get_member_workplaces(member.id)


@injection_test
def test_no_company_workers_are_returned_for_fresh_company(
    company_generator: CompanyGenerator,
    repo: CompanyWorkerRepository,
):
    company = company_generator.create_company()
    assert not repo.get_company_workers(company)


@injection_test
def test_worker_that_was_added_shows_up_in_company_workers(
    company_generator: CompanyGenerator,
    member_generator: MemberGenerator,
    repo: CompanyWorkerRepository,
):
    company = company_generator.create_company()
    member = member_generator.create_member()
    repo.add_worker_to_company(company=company, worker=member)
    assert member in repo.get_company_workers(company)
