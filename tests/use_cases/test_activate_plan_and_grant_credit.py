from decimal import Decimal
from uuid import uuid4

import pytest

from arbeitszeit.entities import ProductionCosts
from arbeitszeit.use_cases import ActivatePlanAndGrantCredit

from ..data_generators import PlanGenerator
from .dependency_injection import injection_test
from .repositories import AccountRepository


@injection_test
def test_that_non_existing_plan_id_raises_assertion_error(
    activate_plan: ActivatePlanAndGrantCredit,
):
    with pytest.raises(AssertionError, match="Plan does not exist"):
        activate_plan(uuid4())


@injection_test
def test_that_a_nonapproved_plan_raises_assertion_error_and_does_not_get_activated(
    activate_plan: ActivatePlanAndGrantCredit, plan_generator: PlanGenerator
):
    plan = plan_generator.create_plan()
    plan.approved = False
    with pytest.raises(AssertionError, match="Plan has not been approved"):
        activate_plan(plan.id)
    assert not plan.is_active


@injection_test
def test_that_approved_plans_gets_activated(
    activate_plan: ActivatePlanAndGrantCredit, plan_generator: PlanGenerator
):
    plan = plan_generator.create_plan(approved=True)
    activate_plan(plan.id)
    assert plan.is_active


@injection_test
def test_that_means_of_production_are_transfered(
    activate_plan: ActivatePlanAndGrantCredit,
    plan_generator: PlanGenerator,
    account_repo: AccountRepository,
):
    plan = plan_generator.create_plan(
        approved=True, costs=ProductionCosts(Decimal(0), Decimal(0), Decimal(5))
    )
    activate_plan(plan.id)
    assert account_repo.get_account_balance(plan.planner.means_account) == 5


@injection_test
def test_that_means_of_production_costs_are_correctly_rounded_and_transfered(
    activate_plan: ActivatePlanAndGrantCredit,
    plan_generator: PlanGenerator,
    account_repo: AccountRepository,
):
    plan = plan_generator.create_plan(
        approved=True, costs=ProductionCosts(Decimal(0), Decimal(0), Decimal(5.155))
    )
    activate_plan(plan.id)
    assert str(account_repo.get_account_balance(plan.planner.means_account)) == "5.16"


@injection_test
def test_that_raw_material_costs_are_transfered(
    activate_plan: ActivatePlanAndGrantCredit,
    plan_generator: PlanGenerator,
    account_repo: AccountRepository,
):
    plan = plan_generator.create_plan(
        approved=True, costs=ProductionCosts(Decimal(0), Decimal(5), Decimal(0))
    )
    activate_plan(plan.id)
    assert account_repo.get_account_balance(plan.planner.raw_material_account) == 5


@injection_test
def test_that_no_labour_costs_are_transfered(
    activate_plan: ActivatePlanAndGrantCredit,
    plan_generator: PlanGenerator,
    account_repo: AccountRepository,
):
    plan = plan_generator.create_plan(
        approved=True, costs=ProductionCosts(Decimal(10), Decimal(10), Decimal(10))
    )
    activate_plan(plan.id)
    assert account_repo.get_account_balance(plan.planner.work_account) == 0


@injection_test
def test_that_product_account_is_adjusted(
    activate_plan: ActivatePlanAndGrantCredit,
    plan_generator: PlanGenerator,
    account_repo: AccountRepository,
):
    plan = plan_generator.create_plan(
        approved=True, costs=ProductionCosts(Decimal(10), Decimal(5), Decimal(2))
    )
    activate_plan(plan.id)
    assert account_repo.get_account_balance(plan.planner.product_account) == -17
