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
