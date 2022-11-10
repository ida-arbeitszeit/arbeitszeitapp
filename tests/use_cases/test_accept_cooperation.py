from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.price_calculator import calculate_price
from arbeitszeit.use_cases import AcceptCooperation, AcceptCooperationRequest
from tests.data_generators import CompanyGenerator, CooperationGenerator, PlanGenerator

from .dependency_injection import injection_test
from .repositories import PlanCooperationRepository


@injection_test
def test_error_is_raised_when_plan_does_not_exist(
    accept_cooperation: AcceptCooperation,
    cooperation_generator: CooperationGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company_entity()
    cooperation = cooperation_generator.create_cooperation(coordinator=requester)
    request = AcceptCooperationRequest(
        requester_id=requester.id, plan_id=uuid4(), cooperation_id=cooperation.id
    )
    response = accept_cooperation(request)
    assert response.is_rejected
    assert response.rejection_reason == response.RejectionReason.plan_not_found


@injection_test
def test_error_is_raised_when_cooperation_does_not_exist(
    accept_cooperation: AcceptCooperation,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company_entity()
    plan = plan_generator.create_plan()
    request = AcceptCooperationRequest(
        requester_id=requester.id, plan_id=plan.id, cooperation_id=uuid4()
    )
    response = accept_cooperation(request)
    assert response.is_rejected
    assert response.rejection_reason == response.RejectionReason.cooperation_not_found


@injection_test
def test_error_is_raised_when_plan_is_already_in_cooperation(
    accept_cooperation: AcceptCooperation,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company_entity()
    cooperation1 = cooperation_generator.create_cooperation()
    cooperation2 = cooperation_generator.create_cooperation(coordinator=requester)
    plan = plan_generator.create_plan(
        activation_date=datetime.now(), cooperation=cooperation1
    )
    request = AcceptCooperationRequest(
        requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation2.id
    )
    response = accept_cooperation(request)
    assert response.is_rejected
    assert response.rejection_reason == response.RejectionReason.plan_has_cooperation


@injection_test
def test_error_is_raised_when_plan_is_public_plan(
    accept_cooperation: AcceptCooperation,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company_entity()
    plan = plan_generator.create_plan(
        activation_date=datetime.now(), is_public_service=True
    )
    cooperation = cooperation_generator.create_cooperation(coordinator=requester)
    request = AcceptCooperationRequest(
        requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
    )
    response = accept_cooperation(request)
    assert response.is_rejected
    assert response.rejection_reason == response.RejectionReason.plan_is_public_service


@injection_test
def test_error_is_raised_when_cooperation_was_not_requested(
    accept_cooperation: AcceptCooperation,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company_entity()
    plan = plan_generator.create_plan(activation_date=datetime.now())
    cooperation = cooperation_generator.create_cooperation(coordinator=requester)
    request = AcceptCooperationRequest(
        requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
    )
    response = accept_cooperation(request)
    assert response.is_rejected
    assert (
        response.rejection_reason
        == response.RejectionReason.cooperation_was_not_requested
    )


@injection_test
def test_error_is_raised_when_requester_is_not_coordinator_of_cooperation(
    accept_cooperation: AcceptCooperation,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company_entity()
    coordinator = company_generator.create_company_entity()
    cooperation = cooperation_generator.create_cooperation(coordinator=coordinator)
    plan = plan_generator.create_plan(
        activation_date=datetime.now(), requested_cooperation=cooperation
    )
    request = AcceptCooperationRequest(
        requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
    )
    response = accept_cooperation(request)
    assert response.is_rejected
    assert (
        response.rejection_reason
        == response.RejectionReason.requester_is_not_coordinator
    )


@injection_test
def test_possible_to_add_plan_to_cooperation(
    accept_cooperation: AcceptCooperation,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company_entity()
    cooperation = cooperation_generator.create_cooperation(coordinator=requester)
    plan = plan_generator.create_plan(
        activation_date=datetime.now(), requested_cooperation=cooperation
    )
    request = AcceptCooperationRequest(
        requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
    )
    response = accept_cooperation(request)
    assert not response.is_rejected


@injection_test
def test_cooperation_is_added_to_plan(
    accept_cooperation: AcceptCooperation,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company_entity()
    cooperation = cooperation_generator.create_cooperation(coordinator=requester)
    plan = plan_generator.create_plan(
        activation_date=datetime.now(), requested_cooperation=cooperation
    )
    request = AcceptCooperationRequest(
        requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
    )
    accept_cooperation(request)
    assert plan.cooperation == cooperation.id


@injection_test
def test_two_cooperating_plans_have_same_prices(
    accept_cooperation: AcceptCooperation,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
    plan_cooperation_repository: PlanCooperationRepository,
):
    requester = company_generator.create_company_entity()
    cooperation = cooperation_generator.create_cooperation(coordinator=requester)
    plan1 = plan_generator.create_plan(
        activation_date=datetime.now(),
        costs=ProductionCosts(Decimal(10), Decimal(20), Decimal(30)),
        requested_cooperation=cooperation,
    )
    plan2 = plan_generator.create_plan(
        activation_date=datetime.now(),
        costs=ProductionCosts(Decimal(1), Decimal(2), Decimal(3)),
        requested_cooperation=cooperation,
    )
    request1 = AcceptCooperationRequest(
        requester_id=requester.id, plan_id=plan1.id, cooperation_id=cooperation.id
    )
    request2 = AcceptCooperationRequest(
        requester_id=requester.id, plan_id=plan2.id, cooperation_id=cooperation.id
    )
    accept_cooperation(request1)
    accept_cooperation(request2)
    assert calculate_price(
        plan_cooperation_repository.get_cooperating_plans(plan1.id)
    ) == calculate_price(plan_cooperation_repository.get_cooperating_plans(plan2.id))


@injection_test
def test_price_of_cooperating_plans_is_correctly_calculated(
    accept_cooperation: AcceptCooperation,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
    plan_cooperation_repository: PlanCooperationRepository,
):
    requester = company_generator.create_company_entity()
    cooperation = cooperation_generator.create_cooperation(coordinator=requester)
    plan1 = plan_generator.create_plan(
        activation_date=datetime.now(),
        costs=ProductionCosts(Decimal(10), Decimal(5), Decimal(5)),
        amount=10,
        requested_cooperation=cooperation,
    )
    plan2 = plan_generator.create_plan(
        activation_date=datetime.now(),
        costs=ProductionCosts(Decimal(5), Decimal(3), Decimal(2)),
        amount=10,
        requested_cooperation=cooperation,
    )
    request1 = AcceptCooperationRequest(
        requester_id=requester.id, plan_id=plan1.id, cooperation_id=cooperation.id
    )
    request2 = AcceptCooperationRequest(
        requester_id=requester.id, plan_id=plan2.id, cooperation_id=cooperation.id
    )
    accept_cooperation(request1)
    accept_cooperation(request2)
    # In total costs of 30h and 20 units -> price should be 1.5h per unit
    assert (
        calculate_price(plan_cooperation_repository.get_cooperating_plans(plan1.id))
        == calculate_price(plan_cooperation_repository.get_cooperating_plans(plan2.id))
        == Decimal("1.5")
    )


@injection_test
def test_that_attribute_requested_cooperation_is_set_to_none_after_start_of_cooperation(
    accept_cooperation: AcceptCooperation,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company_entity()
    cooperation = cooperation_generator.create_cooperation(coordinator=requester)
    plan = plan_generator.create_plan(
        activation_date=datetime.now(), requested_cooperation=cooperation
    )
    request = AcceptCooperationRequest(
        requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
    )
    assert plan.requested_cooperation == cooperation.id
    accept_cooperation(request)
    assert plan.requested_cooperation is None
