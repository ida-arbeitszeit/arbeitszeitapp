from typing import Union
from uuid import UUID, uuid4

from arbeitszeit.entities import Member
from arbeitszeit.use_cases.list_workers import (
    ListWorkers,
    ListWorkersRequest,
    ListWorkersResponse,
)
from tests.data_generators import CompanyGenerator, MemberGenerator

from .dependency_injection import injection_test


def make_request(company: UUID) -> ListWorkersRequest:
    return ListWorkersRequest(company)


def worker_in_results(
    worker: Union[Member, UUID], response: ListWorkersResponse
) -> bool:
    if isinstance(worker, Member):
        worker = worker.id
    return any(w.id == worker for w in response.workers)


@injection_test
def test_list_workers_response_is_empty_for_nonexisting_company(
    list_workers: ListWorkers,
) -> None:
    response: ListWorkersResponse = list_workers(make_request(company=uuid4()))
    assert not response.workers


@injection_test
def test_list_workers_response_is_empty_for_company_without_worker(
    list_workers: ListWorkers,
    company_generator: CompanyGenerator,
) -> None:
    company = company_generator.create_company()
    response = list_workers(make_request(company=company))
    assert not response.workers


@injection_test
def test_list_workers_response_includes_single_company_worker(
    list_workers: ListWorkers,
    company_generator: CompanyGenerator,
    member_generator: MemberGenerator,
) -> None:
    worker = member_generator.create_member()
    company = company_generator.create_company(workers=[worker])
    response = list_workers(make_request(company=company))
    assert worker_in_results(worker, response)


@injection_test
def test_list_workers_response_includes_multiple_company_workers(
    list_workers: ListWorkers,
    company_generator: CompanyGenerator,
    member_generator: MemberGenerator,
) -> None:
    worker1 = member_generator.create_member()
    worker2 = member_generator.create_member()
    company = company_generator.create_company_entity(workers=[worker1, worker2])
    response: ListWorkersResponse = list_workers(make_request(company=company.id))
    assert worker_in_results(worker1, response) and worker_in_results(worker2, response)
