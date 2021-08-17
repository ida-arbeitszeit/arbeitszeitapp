import datetime
from decimal import Decimal

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
def test_that_only_approved_plans_get_set_active(
    plan_generator: PlanGenerator,
    synchronized_plan_activation: SynchronizedPlanActivation,
):
    plan1 = plan_generator.create_plan(approved=False)
    plan2 = plan_generator.create_plan(approved=True)
    synchronized_plan_activation()
    assert not plan1.is_active
    assert plan2.is_active


@injection_test
def test_that_attribute_last_certificate_payout_gets_set(
    plan_generator: PlanGenerator,
    synchronized_plan_activation: SynchronizedPlanActivation,
):
    plan = plan_generator.create_plan(approved=True)
    assert not plan.last_certificate_payout
    synchronized_plan_activation()
    assert plan.last_certificate_payout


@injection_test
def test_account_balances_adjusted_for_p_r_and_prd(
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
    assert account_repository.get_account_balance(plan.planner.product_account) == -(
        plan.expected_sales_value()
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


@injection_test
def test_that_transactions_with_all_four_account_types_as_receivers_are_added_to_repo(
    synchronized_plan_activation: SynchronizedPlanActivation,
    plan_generator: PlanGenerator,
    transaction_repository: TransactionRepository,
):
    plan_generator.create_plan(approved=True)
    synchronized_plan_activation()
    added_account_types = [
        transaction.account_to.account_type
        for transaction in transaction_repository.transactions
    ]
    for expected_account_type in (
        AccountTypes.p,
        AccountTypes.r,
        AccountTypes.a,
        AccountTypes.prd,
    ):
        assert expected_account_type in added_account_types


@injection_test
def test_that_added_transactions_for_p_r_and_prd_have_correct_amounts(
    synchronized_plan_activation: SynchronizedPlanActivation,
    plan_generator: PlanGenerator,
    transaction_repository: TransactionRepository,
):
    plan = plan_generator.create_plan(approved=True)
    expected_amount_p, expected_amount_r, expected_amount_prd = (
        plan.production_costs.means_cost,
        plan.production_costs.resource_cost,
        -plan.expected_sales_value(),
    )
    synchronized_plan_activation()

    for trans in transaction_repository.transactions:
        if trans.account_to.account_type == AccountTypes.p:
            added_amount_p = trans.amount
        elif trans.account_to.account_type == AccountTypes.r:
            added_amount_r = trans.amount
        elif trans.account_to.account_type == AccountTypes.prd:
            added_amount_prd = trans.amount

    assert expected_amount_p == added_amount_p
    assert expected_amount_r == added_amount_r
    assert expected_amount_prd == added_amount_prd


@injection_test
def test_that_added_transactions_for_p_r_and_prd_have_correct_amounts_if_public_plan(
    synchronized_plan_activation: SynchronizedPlanActivation,
    plan_generator: PlanGenerator,
    transaction_repository: TransactionRepository,
):
    plan = plan_generator.create_plan(approved=True, is_public_service=True)
    expected_amount_p, expected_amount_r, expected_amount_prd = (
        plan.production_costs.means_cost,
        plan.production_costs.resource_cost,
        0,
    )
    synchronized_plan_activation()

    for trans in transaction_repository.transactions:
        if trans.account_to.account_type == AccountTypes.p:
            added_amount_p = trans.amount
        elif trans.account_to.account_type == AccountTypes.r:
            added_amount_r = trans.amount
        elif trans.account_to.account_type == AccountTypes.prd:
            added_amount_prd = trans.amount

    assert expected_amount_p == added_amount_p
    assert expected_amount_r == added_amount_r
    assert expected_amount_prd == added_amount_prd


@injection_test
def test_that_wages_are_paid_out(
    synchronized_plan_activation: SynchronizedPlanActivation,
    plan_generator: PlanGenerator,
    transaction_repository: TransactionRepository,
):
    plan = plan_generator.create_plan(approved=True)
    assert plan.production_costs.labour_cost
    synchronized_plan_activation()
    for trans in transaction_repository.transactions:
        if trans.account_to.account_type == AccountTypes.a:
            assert trans.amount


@injection_test
def test_account_balances_correctly_adjusted_for_work_account(
    plan_generator: PlanGenerator,
    synchronized_plan_activation: SynchronizedPlanActivation,
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
def test_account_balances_correctly_adjusted_for_work_accounts_with_two_plans(
    plan_generator: PlanGenerator,
    synchronized_plan_activation: SynchronizedPlanActivation,
    account_repository: AccountRepository,
):
    plan1 = plan_generator.create_plan(
        approved=True, is_public_service=False, timeframe=5, total_cost=Decimal(3)
    )

    plan2 = plan_generator.create_plan(
        approved=True, is_public_service=False, timeframe=2, total_cost=Decimal(9)
    )

    expected_payout_factor = 1
    expected_payout1 = expected_payout_factor * plan1.production_costs.labour_cost / 5
    expected_payout2 = expected_payout_factor * plan2.production_costs.labour_cost / 2
    synchronized_plan_activation()

    assert (
        account_repository.get_account_balance(plan1.planner.work_account)
        == expected_payout1
    )
    assert (
        account_repository.get_account_balance(plan2.planner.work_account)
        == expected_payout2
    )


@injection_test
def test_account_balances_correctly_adjusted_for_work_accounts_with_public_and_productive_plans_of_different_timeframes(
    plan_generator: PlanGenerator,
    synchronized_plan_activation: SynchronizedPlanActivation,
    account_repository: AccountRepository,
):
    plan1 = plan_generator.create_plan(
        approved=True, is_public_service=False, timeframe=2, total_cost=Decimal(3)
    )

    plan2 = plan_generator.create_plan(
        approved=True, is_public_service=True, timeframe=5, total_cost=Decimal(9)
    )
    # (A − ( P o + R o )) / (A + A o) =
    # (1/2 - (3/5 + 3/5)) / (1/2 + 3/5) =
    # -0.7 / 1.1 = -0.636363636
    expected_payout_factor = Decimal(-0.636363636)
    expected_payout1 = round(
        (expected_payout_factor * plan1.production_costs.labour_cost / plan1.timeframe),
        2,
    )
    expected_payout2 = round(
        (expected_payout_factor * plan2.production_costs.labour_cost / plan2.timeframe),
        2,
    )
    synchronized_plan_activation()

    assert (
        account_repository.get_account_balance(plan1.planner.work_account)
        == expected_payout1
    )
    assert (
        account_repository.get_account_balance(plan2.planner.work_account)
        == expected_payout2
    )


@injection_test
def test_account_balances_correctly_adjusted_with_public_plan_not_yet_activated(
    plan_generator: PlanGenerator,
    synchronized_plan_activation: SynchronizedPlanActivation,
    account_repository: AccountRepository,
    datetime_service: FakeDatetimeService,
):

    plan1 = plan_generator.create_plan(
        approved=True,
        is_public_service=False,
        timeframe=2,
        total_cost=Decimal(3),
    )

    # plan 2 is created after last activation date, and should not influence payout factor
    plan2 = plan_generator.create_plan(
        approved=True,
        is_public_service=True,
        timeframe=5,
        total_cost=Decimal(9),
        plan_creation_date=datetime_service.past_plan_activation_date()
        + datetime.timedelta(hours=1),
        is_active=False,
    )

    expected_payout_factor = Decimal(1)
    expected_payout1 = round(
        (expected_payout_factor * plan1.production_costs.labour_cost / plan1.timeframe),
        2,
    )
    expected_payout2 = 0
    synchronized_plan_activation()

    assert (
        account_repository.get_account_balance(plan1.planner.work_account)
        == expected_payout1
    )
    assert (
        account_repository.get_account_balance(plan2.planner.work_account)
        == expected_payout2
    )


@injection_test
def test_that_wages_are_paid_out_only_once_per_day(
    synchronized_plan_activation: SynchronizedPlanActivation,
    plan_generator: PlanGenerator,
    transaction_repository: TransactionRepository,
    datetime_service: FakeDatetimeService,
):
    datetime_service.freeze_time(datetime.datetime(2021, 1, 1, 1))
    expected_wages_transactions = 1
    wages_transactions = 0
    plan = plan_generator.create_plan(approved=True)
    assert plan.production_costs.labour_cost
    synchronized_plan_activation()
    synchronized_plan_activation()

    datetime_service.freeze_time(datetime.datetime(2021, 1, 1, 20))
    synchronized_plan_activation()

    for trans in transaction_repository.transactions:
        if trans.account_to.account_type == AccountTypes.a:
            wages_transactions += 1
    assert wages_transactions == expected_wages_transactions


@injection_test
def test_that_wages_are_paid_out_twice_after_two_days(
    synchronized_plan_activation: SynchronizedPlanActivation,
    plan_generator: PlanGenerator,
    transaction_repository: TransactionRepository,
    datetime_service: FakeDatetimeService,
):
    datetime_service.freeze_time(datetime.datetime(2021, 1, 1, 1))
    expected_wages_transactions = 2
    wages_transactions = 0
    plan = plan_generator.create_plan(approved=True)
    assert plan.production_costs.labour_cost
    synchronized_plan_activation()
    synchronized_plan_activation()

    datetime_service.freeze_time(datetime.datetime(2021, 1, 2, 20))
    synchronized_plan_activation()

    for trans in transaction_repository.transactions:
        if trans.account_to.account_type == AccountTypes.a:
            wages_transactions += 1
    assert wages_transactions == expected_wages_transactions
