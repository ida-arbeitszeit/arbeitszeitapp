from uuid import uuid4

from arbeitszeit.entities import Company, Member
from arbeitszeit.use_cases import ListWorkers, ListWorkersResponse
from tests.data_generators import CompanyGenerator, MemberGenerator

from .dependency_injection import injection_test


def worker_in_results(worker: Member, response: ListWorkersResponse) -> bool:
    return any(
        (
            worker.id == result.id
            and worker.name == result.name
            and worker.email == result.email
            for result in response.workers
        )
    )


@injection_test
def test_list_workers_response_is_empty_for_nonexisting_company(
    list_workers: ListWorkers,
):
    response: ListWorkersResponse = list_workers(company_id=uuid4())
    assert not response.workers


@injection_test
def test_list_workers_response_is_empty_for_company_without_worker(
    list_workers: ListWorkers,
    company_generator: CompanyGenerator,
):
    company: Company = company_generator.create_company()
    response: ListWorkersResponse = list_workers(company_id=company.id)
    assert not response.workers


@injection_test
def test_list_workers_response_includes_single_company_worker(
    list_workers: ListWorkers,
    company_generator: CompanyGenerator,
    member_generator: MemberGenerator,
):
    worker: Member = member_generator.create_member()
    company: Company = company_generator.create_company(workers=[worker])
    response: ListWorkersResponse = list_workers(company_id=company.id)
    assert worker_in_results(worker, response)


@injection_test
def test_list_workers_response_includes_multiple_company_workers(
    list_workers: ListWorkers,
    company_generator: CompanyGenerator,
    member_generator: MemberGenerator,
):
    worker1: Member = member_generator.create_member()
    worker2: Member = member_generator.create_member()
    company: Company = company_generator.create_company(workers=[worker1, worker2])
    response: ListWorkersResponse = list_workers(company_id=company.id)
    assert worker_in_results(worker1, response) and worker_in_results(worker2, response)
