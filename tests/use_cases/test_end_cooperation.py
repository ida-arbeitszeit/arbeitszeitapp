from uuid import uuid4

from arbeitszeit.use_cases import (
    EndCooperation,
    EndCooperationRequest,
    EndCooperationResponse,
)
from tests.data_generators import CooperationGenerator, PlanGenerator

from .dependency_injection import injection_test
from .repositories import CooperationRepository


@injection_test
def test_error_is_raised_when_plan_does_not_exist(
    end_cooperation: EndCooperation, coop_generator: CooperationGenerator
):
    cooperation = coop_generator.create_cooperation()
    request = EndCooperationRequest(plan_id=uuid4(), cooperation_id=cooperation.id)
    response = end_cooperation(request)
    assert response.is_rejected
    assert (
        response.rejection_reason
        == EndCooperationResponse.RejectionReason.plan_not_found
    )


@injection_test
def test_error_is_raised_when_cooperation_does_not_exist(
    end_cooperation: EndCooperation, plan_generator: PlanGenerator
):
    plan = plan_generator.create_plan()
    request = EndCooperationRequest(plan_id=plan.id, cooperation_id=uuid4())
    response = end_cooperation(request)
    assert response.is_rejected
    assert (
        response.rejection_reason
        == EndCooperationResponse.RejectionReason.cooperation_not_found
    )


@injection_test
def test_error_is_raised_when_plan_has_no_cooperation(
    end_cooperation: EndCooperation,
    plan_generator: PlanGenerator,
    coop_generator: CooperationGenerator,
):
    cooperation = coop_generator.create_cooperation()
    plan = plan_generator.create_plan(cooperation=None)
    request = EndCooperationRequest(plan_id=plan.id, cooperation_id=cooperation.id)
    response = end_cooperation(request)
    assert response.is_rejected
    assert (
        response.rejection_reason
        == EndCooperationResponse.RejectionReason.plan_has_no_cooperation
    )


@injection_test
def test_error_is_raised_when_plan_is_not_registered_in_cooperation(
    end_cooperation: EndCooperation,
    plan_generator: PlanGenerator,
    coop_generator: CooperationGenerator,
):
    plan = plan_generator.create_plan(cooperation=coop_generator.create_cooperation())
    cooperation = coop_generator.create_cooperation(plans=[])
    request = EndCooperationRequest(plan_id=plan.id, cooperation_id=cooperation.id)
    response = end_cooperation(request)
    assert response.is_rejected
    assert (
        response.rejection_reason
        == EndCooperationResponse.RejectionReason.plan_not_in_cooperation
    )


@injection_test
def test_ending_of_cooperation_is_successful(
    end_cooperation: EndCooperation,
    plan_generator: PlanGenerator,
    coop_generator: CooperationGenerator,
    coop_repo: CooperationRepository,
):
    plan = plan_generator.create_plan()
    cooperation = coop_generator.create_cooperation(plans=[plan])
    coop_repo.add_cooperation_to_plan(plan.id, cooperation.id)

    request = EndCooperationRequest(plan_id=plan.id, cooperation_id=cooperation.id)
    response = end_cooperation(request)
    assert not response.is_rejected


@injection_test
def test_ending_of_cooperation_is_successful_and_plan_deleted_from_coop(
    end_cooperation: EndCooperation,
    plan_generator: PlanGenerator,
    coop_generator: CooperationGenerator,
    coop_repo: CooperationRepository,
):
    plan = plan_generator.create_plan()
    cooperation = coop_generator.create_cooperation(plans=[plan])
    coop_repo.add_cooperation_to_plan(plan.id, cooperation.id)
    assert plan in cooperation.plans

    request = EndCooperationRequest(plan_id=plan.id, cooperation_id=cooperation.id)
    response = end_cooperation(request)
    assert not response.is_rejected
    assert plan not in cooperation.plans


@injection_test
def test_ending_of_cooperation_is_successful_and_coop_deleted_from_plan(
    end_cooperation: EndCooperation,
    plan_generator: PlanGenerator,
    coop_generator: CooperationGenerator,
    coop_repo: CooperationRepository,
):
    plan = plan_generator.create_plan()
    cooperation = coop_generator.create_cooperation(plans=[plan])
    coop_repo.add_cooperation_to_plan(plan.id, cooperation.id)
    assert plan.cooperation == cooperation

    request = EndCooperationRequest(plan_id=plan.id, cooperation_id=cooperation.id)
    response = end_cooperation(request)
    assert not response.is_rejected
    assert plan.cooperation is None
