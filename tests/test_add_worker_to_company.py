import pytest

from arbeitszeit.errors import (
    CompanyDoesNotExist,
    WorkerAlreadyAtCompany,
    WorkerDoesNotExist,
)
from arbeitszeit.use_cases import add_worker_to_company
from tests.data_generators import CompanyGenerator, MemberGenerator
from tests.dependency_injection import injection_test
from tests.repositories import CompanyWorkerRepository


@injection_test
def test_that_error_is_raised_if_nonexisting_company(
    company_worker_repository: CompanyWorkerRepository,
    member_generator: MemberGenerator,
):
    company = None
    worker = member_generator.create_member()
    with pytest.raises(CompanyDoesNotExist):
        add_worker_to_company(company_worker_repository, company, worker)


@injection_test
def test_that_error_is_raised_if_nonexisting_worker(
    company_worker_repository: CompanyWorkerRepository,
    company_generator: CompanyGenerator,
):
    company = company_generator.create_company()
    worker = None
    with pytest.raises(WorkerDoesNotExist):
        add_worker_to_company(company_worker_repository, company, worker)


@injection_test
def test_that_error_is_raised_if_worker_already_at_company(
    company_worker_repository: CompanyWorkerRepository,
    company_generator: CompanyGenerator,
    member_generator: MemberGenerator,
):
    company = company_generator.create_company()
    worker = member_generator.create_member()
    company_worker_repository.add_worker_to_company(company, worker)
    with pytest.raises(WorkerAlreadyAtCompany):
        add_worker_to_company(company_worker_repository, company, worker)


@injection_test
def test_that_worker_is_added_to_company_worker_repo(
    company_worker_repository: CompanyWorkerRepository,
    company_generator: CompanyGenerator,
    member_generator: MemberGenerator,
):
    company = company_generator.create_company()
    worker = member_generator.create_member()
    add_worker_to_company(company_worker_repository, company, worker)
    assert worker in company.workers
