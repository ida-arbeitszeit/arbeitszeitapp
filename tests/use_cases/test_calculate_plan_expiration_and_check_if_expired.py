import datetime

from arbeitszeit.use_cases import CalculatePlanExpirationAndCheckIfExpired
from tests.data_generators import OfferGenerator, PlanGenerator
from tests.datetime_service import FakeDatetimeService
from tests.use_cases.repositories import OfferRepository

from .dependency_injection import injection_test


@injection_test
def test_that_a_plan_that_is_not_active_can_not_expire(
    plan_generator: PlanGenerator,
    calculate_expiration: CalculatePlanExpirationAndCheckIfExpired,
):
    plan = plan_generator.create_plan()
    calculate_expiration()
    assert not plan.expired


@injection_test
def test_that_expiration_time_is_set_if_plan_is_active(
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
    calculate_expiration: CalculatePlanExpirationAndCheckIfExpired,
):
    plan = plan_generator.create_plan(
        timeframe=2, activation_date=datetime_service.now()
    )

    assert not plan.expiration_date
    assert not plan.expiration_relative
    calculate_expiration()
    assert plan.expiration_relative
    assert plan.expiration_date


@injection_test
def test_that_expiration_date_is_correctly_calculated_if_freezed_after_fixed_activation_time(
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
    calculate_expiration: CalculatePlanExpirationAndCheckIfExpired,
):
    # time freezed 1 hour after fixed plan activation time
    datetime_service.freeze_time(
        datetime.datetime(
            2021, 8, 17, datetime_service.hour_of_synchronized_plan_activation + 1
        )
    )

    # plan was activated 1 day before (after fixed activation date)
    plan = plan_generator.create_plan(
        timeframe=1, activation_date=datetime_service.now_minus_one_day()
    )
    calculate_expiration()

    # expected to expire today
    expected_expiration_date = datetime.datetime(
        datetime_service.today().year,
        datetime_service.today().month,
        datetime_service.today().day,
        datetime_service.hour_of_synchronized_plan_activation,
    )
    assert plan.expiration_date == expected_expiration_date

    # plan was activated 10 days before (after fixed activation date)
    plan = plan_generator.create_plan(
        timeframe=1, activation_date=datetime_service.now_minus_ten_days()
    )
    calculate_expiration()

    # expected to expire 9 days ago
    expected_expiration_date = datetime.datetime(
        datetime_service.today().year,
        datetime_service.today().month,
        datetime_service.today().day - 9,
        datetime_service.hour_of_synchronized_plan_activation,
    )
    assert plan.expiration_date == expected_expiration_date


@injection_test
def test_that_expiration_date_is_correctly_calculated_if_freezed_before_fixed_activation_time(
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
    calculate_expiration: CalculatePlanExpirationAndCheckIfExpired,
):
    # time freezed 1 hour before fixed plan activation time
    datetime_service.freeze_time(
        datetime.datetime(
            2021, 8, 17, datetime_service.hour_of_synchronized_plan_activation - 1
        )
    )

    # plan was activated 1 day before (before fixed activation date)
    plan = plan_generator.create_plan(
        timeframe=1, activation_date=datetime_service.now_minus_one_day()
    )
    calculate_expiration()

    # expected to expire today
    expected_expiration_date = datetime.datetime(
        datetime_service.today().year,
        datetime_service.today().month,
        datetime_service.today().day,
        datetime_service.hour_of_synchronized_plan_activation,
    )
    assert plan.expiration_date == expected_expiration_date

    # plan was activated 10 days before (before fixed activation date)
    plan = plan_generator.create_plan(
        timeframe=1, activation_date=datetime_service.now_minus_ten_days()
    )
    calculate_expiration()

    # expected to expire 9 days ago
    expected_expiration_date = datetime.datetime(
        datetime_service.today().year,
        datetime_service.today().month,
        datetime_service.today().day - 9,
        datetime_service.hour_of_synchronized_plan_activation,
    )
    assert plan.expiration_date == expected_expiration_date


@injection_test
def test_that_expiration_relative_is_correctly_calculated_if_freezed_after_fixed_activation_time(
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
    calculate_expiration: CalculatePlanExpirationAndCheckIfExpired,
):
    datetime_service.freeze_time(
        datetime.datetime(
            2021, 8, 17, datetime_service.hour_of_synchronized_plan_activation + 1
        )
    )

    plan = plan_generator.create_plan(
        timeframe=1, activation_date=datetime_service.now_minus_one_day()
    )
    calculate_expiration()
    expected_expiration_relative = -1
    assert plan.expiration_relative == expected_expiration_relative

    plan = plan_generator.create_plan(
        timeframe=1, activation_date=datetime_service.now_minus_ten_days()
    )
    calculate_expiration()
    expected_expiration_relative = -10
    assert plan.expiration_relative == expected_expiration_relative


@injection_test
def test_that_expiration_relative_is_correctly_calculated_if_freezed_before_fixed_activation_time(
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
    calculate_expiration: CalculatePlanExpirationAndCheckIfExpired,
):
    datetime_service.freeze_time(
        datetime.datetime(
            2021, 8, 17, datetime_service.hour_of_synchronized_plan_activation - 1
        )
    )

    plan = plan_generator.create_plan(
        timeframe=1, activation_date=datetime_service.now_minus_one_day()
    )
    calculate_expiration()
    expected_expiration_relative = 0
    assert plan.expiration_relative == expected_expiration_relative

    plan = plan_generator.create_plan(
        timeframe=1, activation_date=datetime_service.now_minus_ten_days()
    )
    calculate_expiration()
    expected_expiration_relative = -9
    assert plan.expiration_relative == expected_expiration_relative


@injection_test
def test_that_plan_is_not_set_to_expired_if_still_in_timeframe(
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
    calculate_expiration: CalculatePlanExpirationAndCheckIfExpired,
):
    datetime_service.freeze_time(
        datetime.datetime(
            2021, 8, 17, datetime_service.hour_of_synchronized_plan_activation - 1
        )
    )

    plan = plan_generator.create_plan(
        timeframe=1, activation_date=datetime_service.now_minus_one_day()
    )
    calculate_expiration()
    assert not plan.expired


@injection_test
def test_that_plan_is_set_to_expired_if_timeframe_is_expired(
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
    calculate_expiration: CalculatePlanExpirationAndCheckIfExpired,
):
    datetime_service.freeze_time(
        datetime.datetime(
            2021, 8, 17, datetime_service.hour_of_synchronized_plan_activation + 1
        )
    )

    plan = plan_generator.create_plan(
        timeframe=1, activation_date=datetime_service.now_minus_one_day()
    )
    calculate_expiration()
    assert plan.expired


@injection_test
def test_that_all_associated_offers_are_deleted_when_plan_is_expired(
    plan_generator: PlanGenerator,
    offer_generator: OfferGenerator,
    offer_repository: OfferRepository,
    datetime_service: FakeDatetimeService,
    calculate_expiration: CalculatePlanExpirationAndCheckIfExpired,
):
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_ten_days(), timeframe=1
    )
    offer_generator.create_offer(plan=plan)
    offer_generator.create_offer(plan=plan)
    assert len(offer_repository.offers) == 2
    calculate_expiration()
    assert len(offer_repository.offers) == 0


@injection_test
def test_that_associated_offers_are_not_deleted_when_plan_is_not_expired(
    plan_generator: PlanGenerator,
    offer_generator: OfferGenerator,
    offer_repository: OfferRepository,
    datetime_service: FakeDatetimeService,
    calculate_expiration: CalculatePlanExpirationAndCheckIfExpired,
):
    plan = plan_generator.create_plan(
        activation_date=datetime_service.now_minus_one_day(), timeframe=3
    )
    offer_generator.create_offer(plan=plan)
    offer_generator.create_offer(plan=plan)
    assert len(offer_repository.offers) == 2
    calculate_expiration()
    assert len(offer_repository.offers) == 2


@injection_test
def test_that_only_offers_associated_with_expired_plans_are_deleted(
    plan_generator: PlanGenerator,
    offer_generator: OfferGenerator,
    offer_repository: OfferRepository,
    datetime_service: FakeDatetimeService,
    calculate_expiration: CalculatePlanExpirationAndCheckIfExpired,
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
    calculate_expiration()
    assert len(offer_repository.offers) == 1
    assert offer_repository.offers[0].id == active_offer.id
