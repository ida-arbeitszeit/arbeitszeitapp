from datetime import datetime
from decimal import Decimal
from uuid import uuid4

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.use_cases import StartCooperation, StartCooperationRequest
from tests.data_generators import CompanyGenerator, CooperationGenerator, PlanGenerator

from .dependency_injection import injection_test


@injection_test
def test_error_is_raised_when_plan_does_not_exist(
    start_cooperation: StartCooperation,
    cooperation_generator: CooperationGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company()
    cooperation = cooperation_generator.create_cooperation(coordinator=requester)
    request = StartCooperationRequest(
        requester_id=requester.id, plan_id=uuid4(), cooperation_id=cooperation.id
    )
    response = start_cooperation(request)
    assert response.is_rejected
    assert response.rejection_reason == response.RejectionReason.plan_not_found


@injection_test
def test_error_is_raised_when_cooperation_does_not_exist(
    start_cooperation: StartCooperation,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company()
    plan = plan_generator.create_plan()
    request = StartCooperationRequest(
        requester_id=requester.id, plan_id=plan.id, cooperation_id=uuid4()
    )
    response = start_cooperation(request)
    assert response.is_rejected
    assert response.rejection_reason == response.RejectionReason.cooperation_not_found


@injection_test
def test_error_is_raised_when_plan_is_not_active(
    start_cooperation: StartCooperation,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company()
    cooperation = cooperation_generator.create_cooperation(coordinator=requester)
    plan = plan_generator.create_plan(activation_date=None)
    request = StartCooperationRequest(
        requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
    )
    response = start_cooperation(request)
    assert response.is_rejected
    assert response.rejection_reason == response.RejectionReason.plan_inactive


@injection_test
def test_error_is_raised_when_plan_is_already_in_cooperation(
    start_cooperation: StartCooperation,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company()
    cooperation1 = cooperation_generator.create_cooperation()
    cooperation2 = cooperation_generator.create_cooperation(coordinator=requester)
    plan = plan_generator.create_plan(
        activation_date=datetime.now(), cooperation=cooperation1
    )
    request = StartCooperationRequest(
        requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation2.id
    )
    response = start_cooperation(request)
    assert response.is_rejected
    assert response.rejection_reason == response.RejectionReason.plan_has_cooperation


@injection_test
def test_error_is_raised_when_plan_is_already_in_the_list_of_associated_plans(
    start_cooperation: StartCooperation,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company()
    plan = plan_generator.create_plan(activation_date=datetime.now())
    cooperation = cooperation_generator.create_cooperation(
        coordinator=requester, plans=[plan]
    )
    request = StartCooperationRequest(
        requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
    )
    response = start_cooperation(request)
    assert response.is_rejected
    assert (
        response.rejection_reason
        == response.RejectionReason.plan_already_part_of_cooperation
    )


@injection_test
def test_error_is_raised_when_plan_is_public_plan(
    start_cooperation: StartCooperation,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company()
    plan = plan_generator.create_plan(
        activation_date=datetime.now(), is_public_service=True
    )
    cooperation = cooperation_generator.create_cooperation(coordinator=requester)
    request = StartCooperationRequest(
        requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
    )
    response = start_cooperation(request)
    assert response.is_rejected
    assert response.rejection_reason == response.RejectionReason.plan_is_public_service


@injection_test
def test_error_is_raised_when_cooeration_was_not_requested(
    start_cooperation: StartCooperation,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company()
    plan = plan_generator.create_plan(activation_date=datetime.now())
    cooperation = cooperation_generator.create_cooperation(coordinator=requester)
    request = StartCooperationRequest(
        requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
    )
    response = start_cooperation(request)
    assert response.is_rejected
    assert (
        response.rejection_reason
        == response.RejectionReason.cooperation_was_not_requested
    )


@injection_test
def test_error_is_raised_when_requester_is_not_coordinator_of_cooperation(
    start_cooperation: StartCooperation,
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
    request = StartCooperationRequest(
        requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
    )
    response = start_cooperation(request)
    assert response.is_rejected
    assert (
        response.rejection_reason
        == response.RejectionReason.requester_is_not_coordinator
    )


@injection_test
def test_possible_to_add_plan_to_cooperation(
    start_cooperation: StartCooperation,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company()
    cooperation = cooperation_generator.create_cooperation(coordinator=requester)
    plan = plan_generator.create_plan(
        activation_date=datetime.now(), requested_cooperation=cooperation
    )
    request = StartCooperationRequest(
        requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
    )
    response = start_cooperation(request)
    assert not response.is_rejected


@injection_test
def test_cooperation_is_added_to_plan(
    start_cooperation: StartCooperation,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company()
    cooperation = cooperation_generator.create_cooperation(coordinator=requester)
    plan = plan_generator.create_plan(
        activation_date=datetime.now(), requested_cooperation=cooperation
    )
    request = StartCooperationRequest(
        requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
    )
    start_cooperation(request)
    assert plan.cooperation == cooperation


@injection_test
def test_plan_is_added_to_cooperation(
    start_cooperation: StartCooperation,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company()
    cooperation = cooperation_generator.create_cooperation(coordinator=requester)
    plan = plan_generator.create_plan(
        activation_date=datetime.now(), requested_cooperation=cooperation
    )
    request = StartCooperationRequest(
        requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
    )
    start_cooperation(request)
    assert cooperation.plans[0] == plan


@injection_test
def test_two_cooperating_plans_have_same_prices(
    start_cooperation: StartCooperation,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company()
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
    request1 = StartCooperationRequest(
        requester_id=requester.id, plan_id=plan1.id, cooperation_id=cooperation.id
    )
    request2 = StartCooperationRequest(
        requester_id=requester.id, plan_id=plan2.id, cooperation_id=cooperation.id
    )
    start_cooperation(request1)
    start_cooperation(request2)
    assert plan1.price_per_unit == plan2.price_per_unit


@injection_test
def test_price_of_cooperating_plans_is_correctly_calculated(
    start_cooperation: StartCooperation,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company()
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
    request1 = StartCooperationRequest(
        requester_id=requester.id, plan_id=plan1.id, cooperation_id=cooperation.id
    )
    request2 = StartCooperationRequest(
        requester_id=requester.id, plan_id=plan2.id, cooperation_id=cooperation.id
    )
    start_cooperation(request1)
    start_cooperation(request2)
    # In total costs of 30h and 20 units -> price should be 1.5h per unit
    assert plan1.price_per_unit == plan2.price_per_unit == Decimal("1.5")


@injection_test
def test_that_attribute_requested_cooperation_is_set_to_none_after_start_of_cooperation(
    start_cooperation: StartCooperation,
    cooperation_generator: CooperationGenerator,
    plan_generator: PlanGenerator,
    company_generator: CompanyGenerator,
):
    requester = company_generator.create_company()
    cooperation = cooperation_generator.create_cooperation(coordinator=requester)
    plan = plan_generator.create_plan(
        activation_date=datetime.now(), requested_cooperation=cooperation
    )
    request = StartCooperationRequest(
        requester_id=requester.id, plan_id=plan.id, cooperation_id=cooperation.id
    )
    assert plan.requested_cooperation == cooperation
    start_cooperation(request)
    assert plan.requested_cooperation is None
