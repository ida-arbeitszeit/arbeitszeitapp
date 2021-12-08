from datetime import datetime
from decimal import Decimal
from typing import List, Union

from arbeitszeit.entities import Plan, ProductionCosts
from project.database.repositories import (
    CooperationRepository,
    PlanCooperationRepository,
    PlanRepository,
)

from ..data_generators import CompanyGenerator, CooperationGenerator, PlanGenerator
from .dependency_injection import injection_test

Number = Union[int, Decimal]


def production_costs(a: Number, r: Number, p: Number) -> ProductionCosts:
    return ProductionCosts(
        Decimal(a),
        Decimal(r),
        Decimal(p),
    )


def plan_in_list(plan: Plan, plan_list: List[Plan]) -> bool:
    for p in plan_list:
        if p.id == plan.id:
            return True
    return False


@injection_test
def test_that_correct_price_for_plan_is_returned_without_cooperation(
    repository: PlanCooperationRepository, plan_generator: PlanGenerator
):
    plan = plan_generator.create_plan()
    price = repository.get_price_per_unit(plan.id)
    assert price == plan.individual_price_per_unit


@injection_test
def test_that_correct_price_for_plan_is_returned_with_1_cooperating_plan(
    repository: PlanCooperationRepository,
    plan_generator: PlanGenerator,
    cooperation_generator: CooperationGenerator,
):
    coop = cooperation_generator.create_cooperation()
    plan = plan_generator.create_plan(
        activation_date=datetime.min,
        cooperation=coop,
        costs=production_costs(1, 1, 1),
        amount=10,
    )
    calculated_price = repository.get_price_per_unit(plan.id)
    assert calculated_price == plan.individual_price_per_unit


@injection_test
def test_that_correct_price_for_plan_is_returned_with_2_cooperating_plans(
    repository: PlanCooperationRepository,
    plan_generator: PlanGenerator,
    cooperation_generator: CooperationGenerator,
):
    coop = cooperation_generator.create_cooperation()
    plan1 = plan_generator.create_plan(
        activation_date=datetime.min,
        cooperation=coop,
        costs=production_costs(1, 1, 1),
        amount=10,
    )
    plan_generator.create_plan(
        activation_date=datetime.min,
        cooperation=coop,
        costs=production_costs(2, 2, 2),
        amount=10,
    )
    price1 = repository.get_price_per_unit(plan1.id)
    assert price1 == Decimal("0.45")  # costs/amount = 9/20


@injection_test
def test_possible_to_set_and_unset_requested_cooperation_attribute(
    repository: PlanCooperationRepository,
    plan_repository: PlanRepository,
    plan_generator: PlanGenerator,
    cooperation_repository: CooperationRepository,
    company_generator: CompanyGenerator,
):

    cooperation = cooperation_repository.create_cooperation(
        creation_timestamp=datetime.now(),
        name="test name",
        definition="test description",
        coordinator=company_generator.create_company(),
    )
    plan = plan_generator.create_plan()

    repository.set_requested_cooperation(plan.id, cooperation.id)
    plan_from_orm = plan_repository.get_plan_by_id(plan.id)
    assert plan_from_orm
    assert plan_from_orm.requested_cooperation

    repository.set_requested_cooperation_to_none(plan.id)
    plan_from_orm = plan_repository.get_plan_by_id(plan.id)
    assert plan_from_orm
    assert plan_from_orm.requested_cooperation is None


@injection_test
def test_possible_to_add_and_to_remove_plan_to_cooperation(
    repository: PlanCooperationRepository,
    plan_repository: PlanRepository,
    plan_generator: PlanGenerator,
    cooperation_repository: CooperationRepository,
    company_generator: CompanyGenerator,
):

    cooperation = cooperation_repository.create_cooperation(
        creation_timestamp=datetime.now(),
        name="test name",
        definition="test description",
        coordinator=company_generator.create_company(),
    )
    plan = plan_generator.create_plan()

    repository.add_plan_to_cooperation(plan.id, cooperation.id)
    plan_from_orm = plan_repository.get_plan_by_id(plan.id)
    assert plan_from_orm
    assert plan_from_orm.cooperation == cooperation.id

    repository.remove_plan_from_cooperation(plan.id)
    plan_from_orm = plan_repository.get_plan_by_id(plan.id)
    assert plan_from_orm
    assert plan_from_orm.cooperation is None


@injection_test
def test_correct_inbound_requests_are_returned(
    repository: PlanCooperationRepository,
    plan_generator: PlanGenerator,
    cooperation_repository: CooperationRepository,
    company_generator: CompanyGenerator,
):
    coop = cooperation_repository.create_cooperation(
        creation_timestamp=datetime.now(),
        name="test name",
        definition="test description",
        coordinator=company_generator.create_company(),
    )
    requesting_plan1 = plan_generator.create_plan(
        activation_date=datetime.min, requested_cooperation=coop
    )
    requesting_plan2 = plan_generator.create_plan(
        activation_date=datetime.min, requested_cooperation=coop
    )
    plan_generator.create_plan(activation_date=datetime.min, requested_cooperation=None)
    inbound_requests = list(repository.get_inbound_requests(coop.coordinator.id))
    assert len(inbound_requests) == 2
    assert plan_in_list(requesting_plan1, inbound_requests)
    assert plan_in_list(requesting_plan2, inbound_requests)


@injection_test
def test_correct_outbound_requests_are_returned(
    repository: PlanCooperationRepository,
    plan_generator: PlanGenerator,
    cooperation_repository: CooperationRepository,
    company_generator: CompanyGenerator,
):
    planner = company_generator.create_company()
    coop = cooperation_repository.create_cooperation(
        creation_timestamp=datetime.now(),
        name="test name",
        definition="test description",
        coordinator=company_generator.create_company(),
    )
    requesting_plan1 = plan_generator.create_plan(
        activation_date=datetime.min, requested_cooperation=coop, planner=planner
    )
    requesting_plan2 = plan_generator.create_plan(
        activation_date=datetime.min, requested_cooperation=coop, planner=planner
    )
    plan_generator.create_plan(
        activation_date=datetime.min, requested_cooperation=None, planner=planner
    )
    outbound_requests = list(repository.get_outbound_requests(planner.id))
    assert len(outbound_requests) == 2
    assert plan_in_list(requesting_plan1, outbound_requests)
    assert plan_in_list(requesting_plan2, outbound_requests)


@injection_test
def test_plans_in_cooperation_correctly_counted(
    repository: PlanCooperationRepository,
    plan_generator: PlanGenerator,
    cooperation_repository: CooperationRepository,
    company_generator: CompanyGenerator,
):
    coop = cooperation_repository.create_cooperation(
        creation_timestamp=datetime.now(),
        name="test name",
        definition="test description",
        coordinator=company_generator.create_company(),
    )
    plan_generator.create_plan(activation_date=datetime.min, cooperation=coop)
    plan_generator.create_plan(activation_date=datetime.min, cooperation=coop)
    plan_generator.create_plan(activation_date=datetime.min, requested_cooperation=None)
    count = repository.count_plans_in_cooperation(coop.id)
    assert count == 2
