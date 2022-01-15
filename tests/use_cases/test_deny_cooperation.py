from datetime import datetime
from uuid import uuid4

from arbeitszeit.use_cases import (
    DenyCooperation,
    DenyCooperationRequest,
    DenyCooperationResponse,
    RequestCooperation,
    RequestCooperationRequest,
)
from tests.data_generators import CompanyGenerator, CooperationGenerator, PlanGenerator

from .dependency_injection import injection_test


@injection_test
def test_error_is_raises_when_plan_does_not_exist(
    deny_cooperation: DenyCooperation,
    company_generator: CompanyGenerator,
    cooperation_generator: CooperationGenerator,
):
    requester = company_generator.create_company()
    cooperation = cooperation_generator.create_cooperation(coordinator=requester)
    request = DenyCooperationRequest(
        requester_id=requester.id, plan_id=uuid4(), cooperation_id=cooperation.id
    )
    response = deny_cooperation(request)
    assert response.is_rejected
    assert (
        response.rejection_reason
        == DenyCooperationResponse.RejectionReason.plan_not_found
    )


@injection_test
def test_error_is_raised_when_cooperation_does_not_exist(
    deny_cooperation: DenyCooperation,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company()
    plan = plan_generator.create_plan()
    request = DenyCooperationRequest(
        requester_id=requester.id, plan_id=plan.id, cooperation_id=uuid4()
    )
    response = deny_cooperation(request)
    assert response.is_rejected
    assert response.rejection_reason == response.RejectionReason.cooperation_not_found


@injection_test
def test_error_is_raised_when_cooperation_was_not_requested(
    deny_cooperation: DenyCooperation,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company()
    plan = plan_generator.create_plan(activation_date=datetime.now())
    cooperation = cooperation_generator.create_cooperation(coordinator=requester)
    request = DenyCooperationRequest(
        requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
    )
    response = deny_cooperation(request)
    assert response.is_rejected
    assert (
        response.rejection_reason
        == response.RejectionReason.cooperation_was_not_requested
    )


@injection_test
def test_error_is_raised_when_requester_is_not_coordinator_of_cooperation(
    deny_cooperation: DenyCooperation,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company()
    coordinator = company_generator.create_company()
    cooperation = cooperation_generator.create_cooperation(coordinator=coordinator)
    plan = plan_generator.create_plan(
        activation_date=datetime.now(), requested_cooperation=cooperation
    )
    request = DenyCooperationRequest(
        requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
    )
    response = deny_cooperation(request)
    assert response.is_rejected
    assert (
        response.rejection_reason
        == response.RejectionReason.requester_is_not_coordinator
    )


@injection_test
def test_possible_to_deny_cooperation(
    deny_cooperation: DenyCooperation,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company()
    cooperation = cooperation_generator.create_cooperation(coordinator=requester)
    plan = plan_generator.create_plan(
        activation_date=datetime.now(), requested_cooperation=cooperation
    )
    request = DenyCooperationRequest(
        requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
    )
    response = deny_cooperation(request)
    assert not response.is_rejected


@injection_test
def test_possible_to_request_cooperation_again_after_cooperation_has_been_denied(
    deny_cooperation: DenyCooperation,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
    request_cooperation: RequestCooperation,
):
    requester = company_generator.create_company()
    cooperation = cooperation_generator.create_cooperation(coordinator=requester)
    plan = plan_generator.create_plan(
        activation_date=datetime.now(), requested_cooperation=cooperation
    )
    request = DenyCooperationRequest(
        requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
    )
    deny_cooperation(request)

    request_request = RequestCooperationRequest(
        requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
    )
    request_cooperation(request_request)
