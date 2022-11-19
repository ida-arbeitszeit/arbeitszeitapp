from datetime import datetime
from decimal import Decimal
from typing import List, Union

from arbeitszeit.entities import Plan, ProductionCosts
from arbeitszeit_flask.database.repositories import (
    CooperationRepository,
    PlanCooperationRepository,
    PlanRepository,
)

from ..data_generators import CompanyGenerator, PlanGenerator
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
        coordinator=company_generator.create_company_entity(),
    )
    plan = plan_generator.create_plan()

    repository.set_requested_cooperation(plan.id, cooperation.id)
    plan_from_orm = plan_repository.get_plans().with_id(plan.id).first()
    assert plan_from_orm
    assert plan_from_orm.requested_cooperation

    repository.set_requested_cooperation_to_none(plan.id)
    plan_from_orm = plan_repository.get_plans().with_id(plan.id).first()
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
        coordinator=company_generator.create_company_entity(),
    )
    plan = plan_generator.create_plan()

    repository.add_plan_to_cooperation(plan.id, cooperation.id)
    plan_from_orm = plan_repository.get_plans().with_id(plan.id).first()
    assert plan_from_orm
    assert plan_from_orm.cooperation == cooperation.id

    repository.remove_plan_from_cooperation(plan.id)
    plan_from_orm = plan_repository.get_plans().with_id(plan.id).first()
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
        coordinator=company_generator.create_company_entity(),
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
        coordinator=company_generator.create_company_entity(),
    )
    plan_generator.create_plan(activation_date=datetime.min, cooperation=coop)
    plan_generator.create_plan(activation_date=datetime.min, cooperation=coop)
    plan_generator.create_plan(activation_date=datetime.min, requested_cooperation=None)
    count = repository.count_plans_in_cooperation(coop.id)
    assert count == 2


@injection_test
def test_only_cooperating_plans_are_returned(
    repository: PlanCooperationRepository,
    plan_generator: PlanGenerator,
    cooperation_repository: CooperationRepository,
    company_generator: CompanyGenerator,
):
    coop = cooperation_repository.create_cooperation(
        creation_timestamp=datetime.now(),
        name="test name",
        definition="test description",
        coordinator=company_generator.create_company_entity(),
    )
    plan1 = plan_generator.create_plan(activation_date=datetime.min, cooperation=coop)
    plan2 = plan_generator.create_plan(activation_date=datetime.min, cooperation=coop)
    plan_generator.create_plan(activation_date=datetime.min, requested_cooperation=None)
    cooperating_plans = repository.get_cooperating_plans(plan1.id)
    assert len(cooperating_plans) == 2
    assert plan_in_list(plan1, cooperating_plans)
    assert plan_in_list(plan2, cooperating_plans)


@injection_test
def test_correct_plans_in_cooperation_returned(
    repository: PlanCooperationRepository,
    plan_generator: PlanGenerator,
    cooperation_repository: CooperationRepository,
    company_generator: CompanyGenerator,
):
    coop = cooperation_repository.create_cooperation(
        creation_timestamp=datetime.now(),
        name="test name",
        definition="test description",
        coordinator=company_generator.create_company_entity(),
    )
    plan1 = plan_generator.create_plan(activation_date=datetime.min, cooperation=coop)
    plan2 = plan_generator.create_plan(activation_date=datetime.min, cooperation=coop)
    plan3 = plan_generator.create_plan(
        activation_date=datetime.min, requested_cooperation=None
    )
    plans = list(repository.get_plans_in_cooperation(coop.id))
    assert len(plans) == 2
    assert plan_in_list(plan1, plans)
    assert plan_in_list(plan2, plans)
    assert not plan_in_list(plan3, plans)


@injection_test
def test_single_plan_is_returned_as_a_1_plan_cooperation(
    repository: PlanCooperationRepository,
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan(activation_date=datetime.min, cooperation=None)
    cooperating_plans = repository.get_cooperating_plans(plan.id)
    assert len(cooperating_plans) == 1
    assert plan_in_list(plan, cooperating_plans)


@injection_test
def test_nothing_returned_when_no_plans_in_cooperation(
    repository: PlanCooperationRepository,
    plan_generator: PlanGenerator,
    cooperation_repository: CooperationRepository,
    company_generator: CompanyGenerator,
):
    coop = cooperation_repository.create_cooperation(
        creation_timestamp=datetime.now(),
        name="test name",
        definition="test description",
        coordinator=company_generator.create_company_entity(),
    )
    plan_generator.create_plan(activation_date=datetime.min, requested_cooperation=None)
    plans = list(repository.get_plans_in_cooperation(coop.id))
    assert len(plans) == 0
