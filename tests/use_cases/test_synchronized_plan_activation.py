import datetime
from decimal import Decimal

from arbeitszeit.entities import AccountTypes, ProductionCosts
from arbeitszeit.use_cases import SynchronizedPlanActivation
from tests.data_generators import PlanGenerator
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import injection_test
from .repositories import AccountRepository, PlanRepository, TransactionRepository


@injection_test
def test_that_attribute_last_certificate_payout_does_not_get_set_if_plan_is_inactive(
    plan_generator: PlanGenerator,
    synchronized_plan_activation: SynchronizedPlanActivation,
):
    plan = plan_generator.create_plan(approved=True, activation_date=None)
    assert not plan.last_certificate_payout
    synchronized_plan_activation()
    assert not plan.last_certificate_payout


@injection_test
def test_that_attribute_last_certificate_payout_does_not_get_set_if_plan_expires_today(
    plan_generator: PlanGenerator,
    synchronized_plan_activation: SynchronizedPlanActivation,
):
    ...


# @injection_test
# def test_that_wages_are_paid_out(
#     synchronized_plan_activation: SynchronizedPlanActivation,
#     plan_generator: PlanGenerator,
#     transaction_repository: TransactionRepository,
# ):
#     plan = plan_generator.create_plan(approved=True)
#     assert plan.production_costs.labour_cost
#     synchronized_plan_activation()
#     for trans in transaction_repository.transactions:
#         if trans.receiving_account.account_type == AccountTypes.a:
#             assert trans.amount


# @injection_test
# def test_account_balances_correctly_adjusted_for_work_account(
#     plan_generator: PlanGenerator,
#     synchronized_plan_activation: SynchronizedPlanActivation,
#     account_repository: AccountRepository,
# ):
#     plan = plan_generator.create_plan(
#         approved=True,
#         is_public_service=False,
#         timeframe=5,
#     )
#     expected_payout_factor = 1
#     expected_payout = expected_payout_factor * plan.production_costs.labour_cost / 5
#     synchronized_plan_activation()

#     assert (
#         account_repository.get_account_balance(plan.planner.work_account)
#         == expected_payout
#     )


# @injection_test
# def test_account_balances_correctly_adjusted_for_work_accounts_with_two_plans(
#     plan_generator: PlanGenerator,
#     synchronized_plan_activation: SynchronizedPlanActivation,
#     account_repository: AccountRepository,
# ):
#     plan1 = plan_generator.create_plan(
#         approved=True,
#         is_public_service=False,
#         timeframe=5,
#         costs=ProductionCosts(Decimal(1), Decimal(1), Decimal(1)),
#     )

#     plan2 = plan_generator.create_plan(
#         approved=True,
#         is_public_service=False,
#         timeframe=2,
#         costs=ProductionCosts(Decimal(3), Decimal(3), Decimal(3)),
#     )

#     expected_payout_factor = 1
#     expected_payout1 = expected_payout_factor * plan1.production_costs.labour_cost / 5
#     expected_payout2 = expected_payout_factor * plan2.production_costs.labour_cost / 2
#     synchronized_plan_activation()

#     assert (
#         account_repository.get_account_balance(plan1.planner.work_account)
#         == expected_payout1
#     )
#     assert (
#         account_repository.get_account_balance(plan2.planner.work_account)
#         == expected_payout2
#     )


# @injection_test
# def test_account_balances_correctly_adjusted_for_work_accounts_with_public_and_productive_plans_of_different_timeframes(
#     plan_generator: PlanGenerator,
#     synchronized_plan_activation: SynchronizedPlanActivation,
#     account_repository: AccountRepository,
# ):
#     plan1 = plan_generator.create_plan(
#         approved=True,
#         is_public_service=False,
#         timeframe=2,
#         costs=ProductionCosts(Decimal(1), Decimal(1), Decimal(1)),
#     )

#     plan2 = plan_generator.create_plan(
#         approved=True,
#         is_public_service=True,
#         timeframe=5,
#         costs=ProductionCosts(Decimal(3), Decimal(3), Decimal(3)),
#     )
#     # (A − ( P o + R o )) / (A + A o) =
#     # (1/2 - (3/5 + 3/5)) / (1/2 + 3/5) =
#     # -0.7 / 1.1 = -0.636363636
#     expected_payout_factor = Decimal(-0.636363636)
#     expected_payout1 = round(
#         (expected_payout_factor * plan1.production_costs.labour_cost / plan1.timeframe),
#         2,
#     )
#     expected_payout2 = round(
#         (expected_payout_factor * plan2.production_costs.labour_cost / plan2.timeframe),
#         2,
#     )
#     synchronized_plan_activation()

#     assert (
#         account_repository.get_account_balance(plan1.planner.work_account)
#         == expected_payout1
#     )
#     assert (
#         account_repository.get_account_balance(plan2.planner.work_account)
#         == expected_payout2
#     )


# @injection_test
# def test_account_balances_correctly_adjusted_with_public_plan_not_yet_activated(
#     plan_generator: PlanGenerator,
#     synchronized_plan_activation: SynchronizedPlanActivation,
#     account_repository: AccountRepository,
#     datetime_service: FakeDatetimeService,
# ):

#     plan1 = plan_generator.create_plan(
#         approved=True,
#         is_public_service=False,
#         timeframe=2,
#         costs=ProductionCosts(Decimal(1), Decimal(1), Decimal(1)),
#     )

#     # plan 2 is created after last activation date, and should not influence payout factor
#     plan2 = plan_generator.create_plan(
#         approved=True,
#         is_public_service=True,
#         timeframe=5,
#         costs=ProductionCosts(Decimal(3), Decimal(3), Decimal(3)),
#         plan_creation_date=datetime_service.past_plan_activation_date()
#         + datetime.timedelta(hours=1),
#     )

#     expected_payout_factor = Decimal(1)
#     expected_payout1 = round(
#         (expected_payout_factor * plan1.production_costs.labour_cost / plan1.timeframe),
#         2,
#     )
#     expected_payout2 = 0
#     synchronized_plan_activation()

#     assert (
#         account_repository.get_account_balance(plan1.planner.work_account)
#         == expected_payout1
#     )
#     assert (
#         account_repository.get_account_balance(plan2.planner.work_account)
#         == expected_payout2
#     )


# @injection_test
# def test_that_wages_are_paid_out_only_once_per_day(
#     synchronized_plan_activation: SynchronizedPlanActivation,
#     plan_generator: PlanGenerator,
#     transaction_repository: TransactionRepository,
#     datetime_service: FakeDatetimeService,
# ):
#     datetime_service.freeze_time(datetime.datetime(2021, 1, 1, 1))
#     expected_wages_transactions = 1
#     wages_transactions = 0
#     plan = plan_generator.create_plan(approved=True)
#     assert plan.production_costs.labour_cost
#     synchronized_plan_activation()
#     synchronized_plan_activation()

#     datetime_service.freeze_time(datetime.datetime(2021, 1, 1, 20))
#     synchronized_plan_activation()

#     for trans in transaction_repository.transactions:
#         if trans.receiving_account.account_type == AccountTypes.a:
#             wages_transactions += 1
#     assert wages_transactions == expected_wages_transactions


# @injection_test
# def test_that_wages_are_paid_out_twice_after_two_days(
#     synchronized_plan_activation: SynchronizedPlanActivation,
#     plan_generator: PlanGenerator,
#     transaction_repository: TransactionRepository,
#     datetime_service: FakeDatetimeService,
# ):
#     datetime_service.freeze_time(datetime.datetime(2021, 1, 1, 1))
#     expected_wages_transactions = 2
#     wages_transactions = 0
#     plan = plan_generator.create_plan(approved=True)
#     assert plan.production_costs.labour_cost
#     synchronized_plan_activation()
#     synchronized_plan_activation()

#     datetime_service.freeze_time(datetime.datetime(2021, 1, 2, 20))
#     synchronized_plan_activation()

#     for trans in transaction_repository.transactions:
#         if trans.receiving_account.account_type == AccountTypes.a:
#             wages_transactions += 1
#     assert wages_transactions == expected_wages_transactions


# @injection_test
# def test_that_wages_are_paid_out_only_once_and_amount_of_wage_is_correct_if_timeframe_is_one_day(
#     synchronized_plan_activation: SynchronizedPlanActivation,
#     plan_generator: PlanGenerator,
#     transaction_repository: TransactionRepository,
#     datetime_service: FakeDatetimeService,
#     account_repository: AccountRepository,
#     plan_repository: PlanRepository,
# ):
#     datetime_service.freeze_time(datetime.datetime(2021, 1, 1, 1))
#     plan = plan_generator.create_plan(
#         approved=True,
#         timeframe=1,
#         costs=ProductionCosts(Decimal(1), Decimal(1), Decimal(1)),
#     )
#     assert plan.production_costs.labour_cost
#     synchronized_plan_activation()

#     datetime_service.freeze_time(datetime.datetime(2021, 1, 2, 20))
#     # plan is now expired
#     plan_repository.set_plan_as_expired(plan)

#     synchronized_plan_activation()

#     expected_wages_transactions = 1
#     wages_transactions = 0
#     expected_balance = 1
#     for trans in transaction_repository.transactions:
#         if trans.receiving_account.account_type == AccountTypes.a:
#             wages_transactions += 1
#     assert (
#         account_repository.get_account_balance(plan.planner.work_account)
#         == expected_balance
#     )
#     assert wages_transactions == expected_wages_transactions
