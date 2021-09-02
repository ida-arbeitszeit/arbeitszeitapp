import datetime

from arbeitszeit.use_cases import CalculatePlanExpirationAndCheckIfExpired
from tests.data_generators import PlanGenerator
from tests.datetime_service import FakeDatetimeService

from .dependency_injection import injection_test


@injection_test
def test_that_a_plan_that_is_not_active_can_not_expire(
    plan_generator: PlanGenerator,
    calculate_plan_expiration_and_check_if_expired: CalculatePlanExpirationAndCheckIfExpired,
):
    plan = plan_generator.create_plan()
    calculate_plan_expiration_and_check_if_expired()
    assert not plan.expired


@injection_test
def test_that_expiration_time_is_set_if_plan_is_active(
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
    calculate_plan_expiration_and_check_if_expired: CalculatePlanExpirationAndCheckIfExpired,
):
    plan = plan_generator.create_plan(
        timeframe=2, activation_date=datetime_service.now()
    )

    assert not plan.expiration_date
    assert not plan.expiration_relative
    calculate_plan_expiration_and_check_if_expired()
    assert plan.expiration_relative
    assert plan.expiration_date


@injection_test
def test_that_expiration_date_is_correctly_calculated_after_fixed_activation_time(
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
    calculate_plan_expiration_and_check_if_expired: CalculatePlanExpirationAndCheckIfExpired,
):
    # time freezed 1 hour after fixed plan activation time
    datetime_service.freeze_time(
        datetime.datetime(
            2021, 8, 17, datetime_service.time_of_synchronized_plan_activation + 1
        )
    )

    # plan was activated 1 day before
    plan = plan_generator.create_plan(
        timeframe=1, activation_date=datetime_service.now_minus_one_day()
    )
    calculate_plan_expiration_and_check_if_expired()

    # expected to expire today
    expected_expiration_date = datetime.datetime(
        datetime_service.today().year,
        datetime_service.today().month,
        datetime_service.today().day,
        datetime_service.time_of_synchronized_plan_activation,
    )
    assert plan.expiration_date == expected_expiration_date


@injection_test
def test_that_expiration_date_is_correctly_calculated_before_fixed_activation_time(
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
    calculate_plan_expiration_and_check_if_expired: CalculatePlanExpirationAndCheckIfExpired,
):
    # time freezed 1 hour before fixed plan activation time
    datetime_service.freeze_time(
        datetime.datetime(
            2021, 8, 17, datetime_service.time_of_synchronized_plan_activation - 1
        )
    )

    # plan was activated 1 day before
    plan = plan_generator.create_plan(
        timeframe=1, activation_date=datetime_service.now_minus_one_day()
    )
    calculate_plan_expiration_and_check_if_expired()

    # expected to expire today
    expected_expiration_date = datetime.datetime(
        datetime_service.today().year,
        datetime_service.today().month,
        datetime_service.today().day,
        datetime_service.time_of_synchronized_plan_activation,
    )
    assert plan.expiration_date == expected_expiration_date


@injection_test
def test_that_expiration_relative_is_correctly_calculated(
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
    calculate_plan_expiration_and_check_if_expired: CalculatePlanExpirationAndCheckIfExpired,
):
    datetime_service.freeze_time(
        datetime.datetime(
            2021, 8, 17, datetime_service.time_of_synchronized_plan_activation + 1
        )
    )

    plan = plan_generator.create_plan(
        timeframe=1, activation_date=datetime_service.now_minus_one_day()
    )
    calculate_plan_expiration_and_check_if_expired()

    expected_expiration_relative = 0
    assert plan.expiration_relative == expected_expiration_relative


@injection_test
def test_that_plan_is_not_set_to_expired_if_still_in_timeframe(
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
    calculate_plan_expiration_and_check_if_expired: CalculatePlanExpirationAndCheckIfExpired,
):
    datetime_service.freeze_time(
        datetime.datetime(
            2021, 8, 17, datetime_service.time_of_synchronized_plan_activation - 1
        )
    )

    plan = plan_generator.create_plan(
        timeframe=1, activation_date=datetime_service.now_minus_one_day()
    )
    calculate_plan_expiration_and_check_if_expired()
    assert not plan.expired


@injection_test
def test_that_plan_is_set_to_expired_if_timeframe_is_expired(
    plan_generator: PlanGenerator,
    datetime_service: FakeDatetimeService,
    calculate_plan_expiration_and_check_if_expired: CalculatePlanExpirationAndCheckIfExpired,
):
    datetime_service.freeze_time(
        datetime.datetime(
            2021, 8, 17, datetime_service.time_of_synchronized_plan_activation + 1
        )
    )

    plan = plan_generator.create_plan(
        timeframe=1, activation_date=datetime_service.now_minus_one_day()
    )
    calculate_plan_expiration_and_check_if_expired()
    assert plan.expired
