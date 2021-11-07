from uuid import uuid4

from arbeitszeit.use_cases import CreateCooperation, CreateCooperationRequest
from tests.data_generators import CompanyGenerator
from tests.use_cases.repositories import CooperationRepository

from .dependency_injection import injection_test


@injection_test
def test_creation_unsuccessfull_when_coordinator_does_not_exist(
    create_cooperation: CreateCooperation,
):
    request = CreateCooperationRequest(
        coordinator_id=uuid4(), name="test name", definition="some info"
    )
    response = create_cooperation(request)
    assert response is None


@injection_test
def test_creation_is_successfull(
    create_cooperation: CreateCooperation,
    company_generator: CompanyGenerator,
):
    coordinator = company_generator.create_company()
    request = CreateCooperationRequest(
        coordinator_id=coordinator.id, name="test name", definition="some info"
    )
    response = create_cooperation(request)
    assert response


@injection_test
def test_creation_creates_a_cooperation_in_repository(
    create_cooperation: CreateCooperation,
    company_generator: CompanyGenerator,
    cooperation_repository: CooperationRepository,
):
    coordinator = company_generator.create_company()
    request = CreateCooperationRequest(
        coordinator_id=coordinator.id, name="test name", definition="some info"
    )
    create_cooperation(request)
    assert len(cooperation_repository) == 1
