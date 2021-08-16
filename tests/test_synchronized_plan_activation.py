from arbeitszeit.entities import AccountTypes
from arbeitszeit.use_cases import SynchronizedPlanActivation
from tests.data_generators import PlanGenerator
from tests.datetime_service import FakeDatetimeService
from tests.dependency_injection import injection_test
from tests.repositories import AccountRepository, TransactionRepository


@injection_test
def test_that_plan_gets_set_active(
    plan_generator: PlanGenerator,
    synchronized_plan_activation: SynchronizedPlanActivation,
):
    plan = plan_generator.create_plan(approved=True)
    assert not plan.is_active
    synchronized_plan_activation()
    assert plan.is_active


@injection_test
def test_account_balances_adjusted_for_p_and_r(
    plan_generator: PlanGenerator,
    synchronized_plan_activation: SynchronizedPlanActivation,
    account_repository: AccountRepository,
):
    plan = plan_generator.create_plan(approved=True)
    synchronized_plan_activation()
    assert (
        account_repository.get_account_balance(plan.planner.means_account)
        == plan.production_costs.means_cost
    )
    assert (
        account_repository.get_account_balance(plan.planner.raw_material_account)
        == plan.production_costs.resource_cost
    )
    # assert plan.planner.work_account.balance == plan.production_costs.labour_cost
    assert account_repository.get_account_balance(plan.planner.product_account) == -(
        plan.expected_sales_value()
    )


@injection_test
def test_account_balances_adjusted_for_a(
    plan_generator: PlanGenerator,
    synchronized_plan_activation: SynchronizedPlanActivation,
    datetime_service: FakeDatetimeService,
    account_repository: AccountRepository,
):
    plan = plan_generator.create_plan(
        approved=True,
        is_public_service=False,
        timeframe=5,
    )
    expected_payout_factor = 1
    expected_payout = expected_payout_factor * plan.production_costs.labour_cost / 5
    synchronized_plan_activation()

    assert (
        account_repository.get_account_balance(plan.planner.work_account)
        == expected_payout
    )


@injection_test
def test_that_all_transactions_have_accounting_as_sender(
    plan_generator: PlanGenerator,
    transaction_repository: TransactionRepository,
    synchronized_plan_activation: SynchronizedPlanActivation,
):
    plan_generator.create_plan(approved=True)
    synchronized_plan_activation()
    for transaction in transaction_repository.transactions:
        assert transaction.account_from.account_type == AccountTypes.accounting


# seek approval

# from datetime import datetime

# from arbeitszeit.entities import AccountTypes
# from arbeitszeit.use_cases import SeekApproval
# from tests.data_generators import PlanGenerator
# from tests.datetime_service import FakeDatetimeService
# from tests.dependency_injection import injection_test
# from tests.repositories import TransactionRepository


# @injection_test
# def test_that_transactions_with_all_four_account_types_as_receivers_are_added_to_repo(
#     seek_approval: SeekApproval,
#     plan_generator: PlanGenerator,
#     transaction_repository: TransactionRepository,
# ):
#     plan = plan_generator.create_plan()
#     seek_approval(plan, None)
#     added_account_types = [
#         transaction.account_to.account_type
#         for transaction in transaction_repository.transactions
#     ]
#     for account_type in (
#         AccountTypes.p,
#         AccountTypes.r,
#         AccountTypes.a,
#         AccountTypes.prd,
#     ):
#         assert account_type in added_account_types


# @injection_test
# def test_that_added_transactions_have_correct_amounts(
#     seek_approval: SeekApproval,
#     plan_generator: PlanGenerator,
#     transaction_repository: TransactionRepository,
# ):
#     plan = plan_generator.create_plan()
#     expected_amount_p, expected_amount_r, expected_amount_a, expected_amount_prd = (
#         plan.production_costs.means_cost,
#         plan.production_costs.resource_cost,
#         plan.production_costs.labour_cost,
#         -plan.production_costs.total_cost(),
#     )
#     seek_approval(plan, None)
#     for trans in transaction_repository.transactions:
#         if trans.account_to.account_type == AccountTypes.p:
#             added_amount_p = trans.amount
#         elif trans.account_to.account_type == AccountTypes.r:
#             added_amount_r = trans.amount
#         elif trans.account_to.account_type == AccountTypes.a:
#             added_amount_a = trans.amount
#         elif trans.account_to.account_type == AccountTypes.prd:
#             added_amount_prd = trans.amount

#     assert expected_amount_p == added_amount_p
#     assert expected_amount_r == added_amount_r
#     assert expected_amount_a == added_amount_a
#     assert expected_amount_prd == added_amount_prd


# import pytest

# from arbeitszeit.entities import AccountTypes
# from arbeitszeit.use_cases import GrantCredit
# from tests.dependency_injection import injection_test
# from tests.repositories import TransactionRepository

# from .data_generators import PlanGenerator


# @injection_test
# def test_that_assertion_error_is_raised_if_plan_has_not_been_approved(
#     grant_credit: GrantCredit,
#     plan_generator: PlanGenerator,
# ):
#     plan = plan_generator.create_plan(approved=False)
#     with pytest.raises(AssertionError):
#         grant_credit(plan)


# @injection_test
# def test_account_balances_adjusted_if_productive_plan(
#     grant_credit: GrantCredit, plan_generator: PlanGenerator
# ):
#     plan = plan_generator.create_plan(approved=True, is_public_service=False)
#     # grant_credit(plan)
#     assert plan.planner.means_account.balance == plan.production_costs.means_cost
#     assert (
#         plan.planner.raw_material_account.balance == plan.production_costs.resource_cost
#     )
#     assert plan.planner.work_account.balance == plan.production_costs.labour_cost
#     assert plan.planner.product_account.balance == -(plan.expected_sales_value())


# @injection_test
# def test_account_balances_adjusted_if_public_service_plan(
#     grant_credit: GrantCredit, plan_generator: PlanGenerator
# ):
#     plan = plan_generator.create_plan(approved=True, is_public_service=True)
#     # grant_credit(plan)
#     assert plan.planner.means_account.balance == plan.production_costs.means_cost
#     assert (
#         plan.planner.raw_material_account.balance == plan.production_costs.resource_cost
#     )
#     assert (
#         plan.planner.work_account.balance
#         == plan.production_costs.labour_cost * grant_credit._calculate_payout_factor()
#     )
#     assert plan.planner.product_account.balance == -(plan.expected_sales_value())


# @injection_test
# def test_that_all_transactions_have_accounting_as_sender(
#     grant_credit: GrantCredit,
#     plan_generator: PlanGenerator,
#     transaction_repository: TransactionRepository,
# ):
#     plan = plan_generator.create_plan(approved=True)
#     grant_credit(plan)
#     for transaction in transaction_repository.transactions:
#         assert transaction.account_from.account_type == AccountTypes.accounting


# @injection_test
# def test_that_transactions_with_all_four_account_types_as_receivers_are_added_to_repo(
#     grant_credit: GrantCredit,
#     plan_generator: PlanGenerator,
#     transaction_repository: TransactionRepository,
# ):
#     plan = plan_generator.create_plan(approved=True)
#     grant_credit(plan)
#     added_account_types = [
#         transaction.account_to.account_type
#         for transaction in transaction_repository.transactions
#     ]
#     for account_type in (
#         AccountTypes.p,
#         AccountTypes.r,
#         AccountTypes.a,
#         AccountTypes.prd,
#     ):
#         assert account_type in added_account_types


# @injection_test
# def test_that_added_transactions_have_correct_amounts_if_productive_plan(
#     grant_credit: GrantCredit,
#     plan_generator: PlanGenerator,
#     transaction_repository: TransactionRepository,
# ):
#     plan = plan_generator.create_plan(approved=True, is_public_service=False)
#     expected_amount_p, expected_amount_r, expected_amount_a, expected_amount_prd = (
#         plan.production_costs.means_cost,
#         plan.production_costs.resource_cost,
#         plan.production_costs.labour_cost,
#         -plan.expected_sales_value(),
#     )
#     grant_credit(plan)
#     for trans in transaction_repository.transactions:
#         if trans.account_to.account_type == AccountTypes.p:
#             added_amount_p = trans.amount
#         elif trans.account_to.account_type == AccountTypes.r:
#             added_amount_r = trans.amount
#         elif trans.account_to.account_type == AccountTypes.a:
#             added_amount_a = trans.amount
#         elif trans.account_to.account_type == AccountTypes.prd:
#             added_amount_prd = trans.amount

#     assert expected_amount_p == added_amount_p
#     assert expected_amount_r == added_amount_r
#     assert expected_amount_a == added_amount_a
#     assert expected_amount_prd == added_amount_prd


# @injection_test
# def test_that_added_transactions_have_correct_amounts_if_public_service_plan(
#     grant_credit: GrantCredit,
#     plan_generator: PlanGenerator,
#     transaction_repository: TransactionRepository,
# ):
#     plan = plan_generator.create_plan(approved=True, is_public_service=True)
#     expected_amount_p, expected_amount_r, expected_amount_a, expected_amount_prd = (
#         plan.production_costs.means_cost,
#         plan.production_costs.resource_cost,
#         plan.production_costs.labour_cost * grant_credit._calculate_payout_factor(),
#         -plan.expected_sales_value(),
#     )
#     grant_credit(plan)
#     for trans in transaction_repository.transactions:
#         if trans.account_to.account_type == AccountTypes.p:
#             added_amount_p = trans.amount
#         elif trans.account_to.account_type == AccountTypes.r:
#             added_amount_r = trans.amount
#         elif trans.account_to.account_type == AccountTypes.a:
#             added_amount_a = trans.amount
#         elif trans.account_to.account_type == AccountTypes.prd:
#             added_amount_prd = trans.amount

#     assert expected_amount_p == added_amount_p
#     assert expected_amount_r == added_amount_r
#     assert expected_amount_a == added_amount_a
#     assert expected_amount_prd == added_amount_prd
