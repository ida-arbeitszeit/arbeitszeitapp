from uuid import uuid4

from arbeitszeit.use_cases import (
    CreateCooperation,
    CreateCooperationRequest,
    CreateCooperationResponse,
)
from tests.data_generators import CompanyGenerator, CooperationGenerator

from .dependency_injection import injection_test


@injection_test
def test_creation_rejected_when_coordinator_does_not_exist(
    create_cooperation: CreateCooperation,
):
    request = CreateCooperationRequest(
        coordinator_id=uuid4(), name="test name", definition="some info"
    )
    response = create_cooperation(request)
    assert response.is_rejected
    assert (
        response.rejection_reason
        == CreateCooperationResponse.RejectionReason.coordinator_not_found
    )


@injection_test
def test_creation_is_rejected_when_coop_name_exists_already(
    create_cooperation: CreateCooperation,
    company_generator: CompanyGenerator,
    cooperation_generator: CooperationGenerator,
):
    cooperation_generator.create_cooperation(name="existing name")
    coordinator = company_generator.create_company()
    request = CreateCooperationRequest(
        coordinator_id=coordinator.id, name="existing name", definition="some info"
    )
    response = create_cooperation(request)
    assert response.is_rejected
    assert (
        response.rejection_reason
        == CreateCooperationResponse.RejectionReason.cooperation_with_name_exists
    )


@injection_test
def test_creation_is_rejected_when_coop_name_exists_with_case_variation(
    create_cooperation: CreateCooperation,
    company_generator: CompanyGenerator,
    cooperation_generator: CooperationGenerator,
):
    cooperation_generator.create_cooperation(name="ExisTing NaMe")
    coordinator = company_generator.create_company()
    request = CreateCooperationRequest(
        coordinator_id=coordinator.id, name="existing name", definition="some info"
    )
    response = create_cooperation(request)
    assert response.is_rejected
    assert (
        response.rejection_reason
        == CreateCooperationResponse.RejectionReason.cooperation_with_name_exists
    )


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
