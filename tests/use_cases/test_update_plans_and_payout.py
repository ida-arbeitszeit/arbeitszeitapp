import datetime
from decimal import Decimal

from arbeitszeit.entities import AccountTypes, ProductionCosts
from arbeitszeit.use_cases import UpdatePlansAndPayout
from tests.data_generators import OfferGenerator, PlanGenerator
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import injection_test
from .repositories import AccountRepository, OfferRepository, TransactionRepository


@injection_test
def test_that_a_plan_that_is_not_active_can_not_expire(
    plan_generator: PlanGenerator,
    payout: UpdatePlansAndPayout,
):
    plan = plan_generator.create_plan()
    payout()
    assert not plan.expired


@injection_test
def test_that_expiration_time_is_set_if_plan_is_active(
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
    payout: UpdatePlansAndPayout,
):
    plan = plan_generator.create_plan(
        timeframe=2, activation_date=datetime_service.now()
    )
    assert not plan.expiration_date
    assert not plan.expiration_relative
    payout()
    assert plan.expiration_relative
    assert plan.expiration_date


@injection_test
def test_that_plan_is_set_expired_and_deactivated_if_expired(
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
    payout: UpdatePlansAndPayout,
):
    plan = plan_generator.create_plan(
        timeframe=5, activation_date=datetime_service.now_minus_ten_days()
    )
    payout()
    assert plan.expired
    assert not plan.is_active


@injection_test
def test_that_plan_is_not_set_to_expired_and_not_deactivated_if_not_yet_expired(
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
    payout: UpdatePlansAndPayout,
):
    plan = plan_generator.create_plan(
        timeframe=5, activation_date=datetime_service.now_minus_one_day()
    )
    payout()
    assert not plan.expired
    assert plan.is_active


@injection_test
def test_that_expiration_date_is_correctly_calculated_if_plan_expires_now(
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
    payout: UpdatePlansAndPayout,
):
    datetime_service.freeze_time(datetime.datetime.now())
    plan = plan_generator.create_plan(
        timeframe=1, activation_date=datetime_service.now_minus_one_day()
    )
    payout()
    expected_expiration_time = datetime_service.now()
    assert plan.expiration_date == expected_expiration_time


@injection_test
def test_that_expiration_date_is_correctly_calculated_if_plan_expires_in_the_future(
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
    payout: UpdatePlansAndPayout,
):
    datetime_service.freeze_time(datetime.datetime.now())
    plan = plan_generator.create_plan(
        timeframe=2, activation_date=datetime_service.now_minus_one_day()
    )
    payout()
    expected_expiration_time = datetime_service.now_plus_one_day()
    assert plan.expiration_date == expected_expiration_time


@injection_test
def test_that_expiration_relative_is_correctly_calculated_when_plan_expires_in_exactly_one_day(
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
    payout: UpdatePlansAndPayout,
):
    datetime_service.freeze_time(datetime.datetime.now())
    plan = plan_generator.create_plan(
        timeframe=2, activation_date=datetime_service.now_minus_one_day()
    )
    payout()
    assert plan.expiration_relative == 1


@injection_test
def test_that_all_associated_offers_are_deleted_when_plan_is_expired(
    plan_generator: PlanGenerator,
    offer_generator: OfferGenerator,
    offer_repository: OfferRepository,
    datetime_service: FakeDatetimeService,
    payout: UpdatePlansAndPayout,
):
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_ten_days(), timeframe=1
    )
    offer_generator.create_offer(plan=plan)
    offer_generator.create_offer(plan=plan)
    assert len(offer_repository.offers) == 2
    payout()
    assert len(offer_repository.offers) == 0


@injection_test
def test_that_associated_offers_are_not_deleted_when_plan_is_not_expired(
    plan_generator: PlanGenerator,
    offer_generator: OfferGenerator,
    offer_repository: OfferRepository,
    datetime_service: FakeDatetimeService,
    payout: UpdatePlansAndPayout,
):
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(), timeframe=3
    )
    offer_generator.create_offer(plan=plan)
    offer_generator.create_offer(plan=plan)
    assert len(offer_repository.offers) == 2
    payout()
    assert len(offer_repository.offers) == 2


@injection_test
def test_that_only_offers_associated_with_expired_plans_are_deleted(
    plan_generator: PlanGenerator,
    offer_generator: OfferGenerator,
    offer_repository: OfferRepository,
    datetime_service: FakeDatetimeService,
    payout: UpdatePlansAndPayout,
):
    active_plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(), timeframe=3
    )
    expired_plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_ten_days(), timeframe=1
    )
    active_offer = offer_generator.create_offer(plan=active_plan)
    offer_generator.create_offer(plan=expired_plan)

    assert len(offer_repository.offers) == 2
    payout()
    assert len(offer_repository.offers) == 1
    assert offer_repository.offers[0].id == active_offer.id


@injection_test
def test_that_wages_are_paid_out(
    payout: UpdatePlansAndPayout,
    plan_generator: PlanGenerator,
    transaction_repository: TransactionRepository,
    account_repository: AccountRepository,
    datetime_service: FakeDatetimeService,
):
    plan = plan_generator.create_plan(
        approved=True, activation_date=datetime_service.now_minus_one_day()
    )
    assert plan.production_costs.labour_cost
    payout()
    assert account_repository.get_account_balance(plan.planner.work_account) != Decimal(
        0
    )


@injection_test
def test_that_wages_do_not_get_paid_out_if_plan_has_expired(
    plan_generator: PlanGenerator,
    payout: UpdatePlansAndPayout,
    datetime_service: FakeDatetimeService,
    account_repository: AccountRepository,
):
    plan = plan_generator.create_plan(
        approved=True,
        activation_date=datetime_service.now_minus_ten_days(),
        timeframe=1,
    )
    payout()
    assert account_repository.get_account_balance(plan.planner.work_account) == 0


@injection_test
def test_that_wages_do_not_get_paid_out_if_plan_expires_later_today(
    plan_generator: PlanGenerator,
    payout: UpdatePlansAndPayout,
    datetime_service: FakeDatetimeService,
    account_repository: AccountRepository,
):
    plan = plan_generator.create_plan(
        approved=True,
        activation_date=datetime_service.now_minus_25_hours(),
        timeframe=1,
    )
    payout()
    assert account_repository.get_account_balance(plan.planner.work_account) == 0


@injection_test
def test_that_attribute_last_certificate_payout_does_not_get_set_if_plan_is_inactive(
    plan_generator: PlanGenerator,
    payout: UpdatePlansAndPayout,
):
    plan = plan_generator.create_plan(approved=True, activation_date=None)
    payout()
    assert not plan.last_certificate_payout


@injection_test
def test_that_attribute_last_certificate_payout_does_not_get_set_if_plan_expires_later_today(
    plan_generator: PlanGenerator,
    payout: UpdatePlansAndPayout,
    datetime_service: FakeDatetimeService,
):
    plan = plan_generator.create_plan(
        approved=True,
        activation_date=datetime_service.now_minus_25_hours(),
        timeframe=1,
    )
    payout()
    assert not plan.last_certificate_payout


@injection_test
def test_account_balances_correctly_adjusted_for_work_account(
    plan_generator: PlanGenerator,
    payout: UpdatePlansAndPayout,
    account_repository: AccountRepository,
    datetime_service: FakeDatetimeService,
):
    plan = plan_generator.create_plan(
        approved=True,
        is_public_service=False,
        activation_date=datetime_service.now_minus_one_day(),
        timeframe=5,
    )
    expected_payout_factor = 1
    expected_payout = expected_payout_factor * plan.production_costs.labour_cost / 5
    payout()

    assert (
        account_repository.get_account_balance(plan.planner.work_account)
        == expected_payout
    )


@injection_test
def test_account_balances_correctly_adjusted_for_work_accounts_with_two_active_plans(
    plan_generator: PlanGenerator,
    payout: UpdatePlansAndPayout,
    datetime_service: FakeDatetimeService,
    account_repository: AccountRepository,
):
    plan1 = plan_generator.create_plan(
        approved=True,
        is_public_service=False,
        timeframe=5,
        activation_date=datetime_service.now_minus_one_day(),
        costs=ProductionCosts(Decimal(1), Decimal(1), Decimal(1)),
    )

    plan2 = plan_generator.create_plan(
        approved=True,
        is_public_service=False,
        timeframe=2,
        activation_date=datetime_service.now_minus_one_day(),
        costs=ProductionCosts(Decimal(3), Decimal(3), Decimal(3)),
    )

    expected_payout_factor = 1
    expected_payout1 = expected_payout_factor * plan1.production_costs.labour_cost / 5
    expected_payout2 = expected_payout_factor * plan2.production_costs.labour_cost / 2
    payout()

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
    payout: UpdatePlansAndPayout,
    account_repository: AccountRepository,
    datetime_service: FakeDatetimeService,
):
    plan1 = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(),
        is_public_service=False,
        timeframe=2,
        costs=ProductionCosts(Decimal(1), Decimal(1), Decimal(1)),
    )

    plan2 = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(),
        is_public_service=True,
        timeframe=5,
        costs=ProductionCosts(Decimal(3), Decimal(3), Decimal(3)),
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
    payout()

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
    payout: UpdatePlansAndPayout,
    account_repository: AccountRepository,
    datetime_service: FakeDatetimeService,
):

    plan1 = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(),
        is_public_service=False,
        timeframe=2,
        costs=ProductionCosts(Decimal(1), Decimal(1), Decimal(1)),
    )

    # plan 2 is created after last activation date, and should not influence payout factor
    plan2 = plan_generator.create_plan(
        approved=True,
        activation_date=None,
        is_public_service=True,
        timeframe=5,
        costs=ProductionCosts(Decimal(3), Decimal(3), Decimal(3)),
    )

    expected_payout_factor = Decimal(1)
    expected_payout1 = round(
        (expected_payout_factor * plan1.production_costs.labour_cost / plan1.timeframe),
        2,
    )
    expected_payout2 = 0
    payout()

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
    payout: UpdatePlansAndPayout,
    plan_generator: PlanGenerator,
    transaction_repository: TransactionRepository,
    datetime_service: FakeDatetimeService,
):
    datetime_service.freeze_time(datetime.datetime(2021, 1, 1, 1))
    expected_wages_transactions = 1
    wages_transactions = 0
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(), timeframe=3
    )
    assert plan.production_costs.labour_cost
    payout()
    payout()

    datetime_service.freeze_time(datetime.datetime(2021, 1, 1, 20))
    payout()

    for trans in transaction_repository.transactions:
        if trans.receiving_account.account_type == AccountTypes.a:
            wages_transactions += 1
    assert wages_transactions == expected_wages_transactions


@injection_test
def test_that_wages_are_paid_out_twice_after_two_days(
    payout: UpdatePlansAndPayout,
    plan_generator: PlanGenerator,
    transaction_repository: TransactionRepository,
    datetime_service: FakeDatetimeService,
):
    datetime_service.freeze_time(datetime.datetime(2021, 1, 1, 1))
    expected_wages_transactions = 2
    wages_transactions = 0
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(), timeframe=3
    )
    assert plan.production_costs.labour_cost
    payout()

    datetime_service.freeze_time(datetime.datetime(2021, 1, 2, 1))
    payout()

    for trans in transaction_repository.transactions:
        if trans.receiving_account.account_type == AccountTypes.a:
            wages_transactions += 1
    assert wages_transactions == expected_wages_transactions


@injection_test
def test_that_wages_are_not_paid_out_on_day_of_plan_expiration(
    payout: UpdatePlansAndPayout,
    plan_generator: PlanGenerator,
    transaction_repository: TransactionRepository,
    datetime_service: FakeDatetimeService,
):
    datetime_service.freeze_time(datetime.datetime(2021, 1, 1, 1))
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_20_hours(),
        timeframe=1,
        costs=ProductionCosts(Decimal(1), Decimal(1), Decimal(1)),
    )
    assert plan.production_costs.labour_cost
    payout()

    expected_wages_transactions = 0
    wages_transactions = 0
    for trans in transaction_repository.transactions:
        if trans.receiving_account.account_type == AccountTypes.a:
            wages_transactions += 1
    assert wages_transactions == expected_wages_transactions
