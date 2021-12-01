from datetime import datetime
from decimal import Decimal
from typing import Union

from arbeitszeit.entities import ProductionCosts
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


@injection_test
def test_that_correct_price_is_returned_without_cooperation(
    repository: PlanCooperationRepository, plan_generator: PlanGenerator
):
    plan = plan_generator.create_plan()
    price = repository.get_price_per_unit(plan.id)
    assert price == plan.individual_price_per_unit


@injection_test
def test_that_correct_price_is_returned_with_cooperation(
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
def test_possible_to_set_requested_cooperation_attribute(
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
