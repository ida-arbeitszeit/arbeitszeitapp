from typing import Union
from uuid import UUID, uuid4

from arbeitszeit.records import Member
from arbeitszeit.use_cases import list_workers
from tests.data_generators import CompanyGenerator, MemberGenerator

from .dependency_injection import injection_test


def make_request(company: UUID) -> list_workers.Request:
    return list_workers.Request(company)


def worker_in_results(
    worker: Union[Member, UUID], response: list_workers.Response
) -> bool:
    if isinstance(worker, Member):
        worker = worker.id
    return any(w.id == worker for w in response.workers)


@injection_test
def test_list_workers_response_is_empty_for_nonexisting_company(
    use_case: list_workers.ListWorkersUseCase,
) -> None:
    response: list_workers.Response = use_case.execute(make_request(company=uuid4()))
    assert not response.workers


@injection_test
def test_list_workers_response_is_empty_for_company_without_worker(
    use_case: list_workers.ListWorkersUseCase,
    company_generator: CompanyGenerator,
) -> None:
    company = company_generator.create_company()
    response = use_case.execute(make_request(company=company))
    assert not response.workers


@injection_test
def test_list_workers_response_includes_single_company_worker(
    use_case: list_workers.ListWorkersUseCase,
    company_generator: CompanyGenerator,
    member_generator: MemberGenerator,
) -> None:
    worker = member_generator.create_member()
    company = company_generator.create_company(workers=[worker])
    response = use_case.execute(make_request(company=company))
    assert worker_in_results(worker, response)


@injection_test
def test_list_workers_response_includes_multiple_company_workers(
    use_case: list_workers.ListWorkersUseCase,
    company_generator: CompanyGenerator,
    member_generator: MemberGenerator,
) -> None:
    worker1 = member_generator.create_member()
    worker2 = member_generator.create_member()
    company = company_generator.create_company_record(workers=[worker1, worker2])
    response: list_workers.Response = use_case.execute(make_request(company=company.id))
    assert worker_in_results(worker1, response) and worker_in_results(worker2, response)
