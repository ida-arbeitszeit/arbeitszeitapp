import datetime

from arbeitszeit.use_cases import calculate_plan_expiration_and_check_if_expired
from tests.data_generators import PlanGenerator
from tests.datetime_service import TestDatetimeService
from tests.dependency_injection import injection_test


@injection_test
def test_that_expiration_info_is_saved_as_instance_attributes(
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan()
    calculate_plan_expiration_and_check_if_expired(plan)
    assert plan.expiration_relative
    assert len(plan.expiration_relative) == 3
    assert plan.expiration_date


@injection_test
def test_that_relative_expiration_time_is_correctly_calculated(
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan(
        plan_creation_date=TestDatetimeService().now(), timeframe=1
    )
    calculate_plan_expiration_and_check_if_expired(plan)
    assert plan.expiration_relative == (0, 23, 59)


@injection_test
def test_that_expiration_date_is_correctly_calculated(
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan(
        plan_creation_date=TestDatetimeService().now(), timeframe=1
    )
    expected_expiration_date = (
        TestDatetimeService().now() + datetime.timedelta(days=1)
    ).strftime("%x")
    calculate_plan_expiration_and_check_if_expired(plan)
    calculated_expiration_date = (
        plan.expiration_date.strftime("%x") if plan.expiration_date else None
    )
    assert expected_expiration_date == calculated_expiration_date


@injection_test
def test_that_plan_is_not_set_to_expired_if_still_in_timeframe(
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan(
        plan_creation_date=TestDatetimeService().now_minus_two_days(), timeframe=3
    )
    calculate_plan_expiration_and_check_if_expired(plan)
    assert not plan.expired


@injection_test
def test_that_plan_is_set_to_expired_if_timeframe_is_expired(
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan(
        plan_creation_date=TestDatetimeService().now_minus_two_days(), timeframe=1
    )
    calculate_plan_expiration_and_check_if_expired(plan)
    assert plan.expired


@injection_test
def test_that_plan_is_only_set_to_expired_if_timeframe_is_expired(
    plan_generator: PlanGenerator,
):
    plan1 = plan_generator.create_plan(
        plan_creation_date=TestDatetimeService().now_minus_two_days(), timeframe=1
    )
    plan2 = plan_generator.create_plan(
        plan_creation_date=TestDatetimeService().now_minus_two_days(), timeframe=3
    )
    calculate_plan_expiration_and_check_if_expired(plan1)
    calculate_plan_expiration_and_check_if_expired(plan2)
    assert plan1.expired
    assert not plan2.expired
