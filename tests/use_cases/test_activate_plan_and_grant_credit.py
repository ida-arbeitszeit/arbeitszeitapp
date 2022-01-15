from decimal import Decimal
from uuid import uuid4

import pytest

from arbeitszeit.entities import AccountTypes, ProductionCosts
from arbeitszeit.use_cases import ActivatePlanAndGrantCredit

from ..data_generators import PlanGenerator
from .dependency_injection import injection_test
from .repositories import AccountRepository, TransactionRepository


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


@injection_test
def test_that_all_transactions_have_accounting_as_sender(
    plan_generator: PlanGenerator,
    transaction_repository: TransactionRepository,
    activate_plan: ActivatePlanAndGrantCredit,
):
    plan = plan_generator.create_plan(approved=True)
    activate_plan(plan.id)
    for transaction in transaction_repository.transactions:
        assert transaction.sending_account.account_type == AccountTypes.accounting


@injection_test
def test_that_transactions_with_all_account_types_except_work_account_as_receivers_are_added_to_repo(
    activate_plan: ActivatePlanAndGrantCredit,
    plan_generator: PlanGenerator,
    transaction_repository: TransactionRepository,
):
    plan = plan_generator.create_plan(approved=True)
    activate_plan(plan.id)
    added_account_types = [
        transaction.receiving_account.account_type
        for transaction in transaction_repository.transactions
    ]
    for expected_account_type in (
        AccountTypes.p,
        AccountTypes.r,
        AccountTypes.prd,
    ):
        assert expected_account_type in added_account_types
    assert AccountTypes.a not in added_account_types


@injection_test
def test_that_added_transactions_for_p_r_and_prd_have_correct_amounts(
    activate_plan: ActivatePlanAndGrantCredit,
    plan_generator: PlanGenerator,
    transaction_repository: TransactionRepository,
):
    plan = plan_generator.create_plan(approved=True)
    expected_amount_p, expected_amount_r, expected_amount_prd = (
        plan.production_costs.means_cost,
        plan.production_costs.resource_cost,
        -plan.expected_sales_value,
    )
    activate_plan(plan.id)

    for trans in transaction_repository.transactions:
        if trans.receiving_account.account_type == AccountTypes.p:
            added_amount_p = trans.amount_received
        elif trans.receiving_account.account_type == AccountTypes.r:
            added_amount_r = trans.amount_received
        elif trans.receiving_account.account_type == AccountTypes.prd:
            added_amount_prd = trans.amount_received

    assert expected_amount_p == added_amount_p
    assert expected_amount_r == added_amount_r
    assert expected_amount_prd == added_amount_prd


@injection_test
def test_that_added_transactions_for_p_r_and_prd_have_correct_amounts_if_public_plan(
    activate_plan: ActivatePlanAndGrantCredit,
    plan_generator: PlanGenerator,
    transaction_repository: TransactionRepository,
):
    plan = plan_generator.create_plan(approved=True, is_public_service=True)
    expected_amount_p, expected_amount_r, expected_amount_prd = (
        plan.production_costs.means_cost,
        plan.production_costs.resource_cost,
        0,
    )
    activate_plan(plan.id)

    for trans in transaction_repository.transactions:
        if trans.receiving_account.account_type == AccountTypes.p:
            added_amount_p = trans.amount_received
        elif trans.receiving_account.account_type == AccountTypes.r:
            added_amount_r = trans.amount_received
        elif trans.receiving_account.account_type == AccountTypes.prd:
            added_amount_prd = trans.amount_received

    assert expected_amount_p == added_amount_p
    assert expected_amount_r == added_amount_r
    assert expected_amount_prd == added_amount_prd
