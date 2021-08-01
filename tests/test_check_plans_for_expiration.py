from arbeitszeit.use_cases import check_plans_for_expiration
from tests.data_generators import PlanGenerator
from tests.datetime_service import TestDatetimeService

from .dependency_injection import injection_test


@injection_test
def test_that_plans_are_not_set_to_expired_if_still_in_timeframe(
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan(
        plan_creation_date=TestDatetimeService().now_minus_two_days(), timeframe=3
    )
    plans = [plan]
    plans = check_plans_for_expiration(plans)
    assert not plans[0].expired


@injection_test
def test_that_plans_are_set_to_expired_if_timeframe_is_expired(
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan(
        plan_creation_date=TestDatetimeService().now_minus_two_days(), timeframe=1
    )
    plans = [plan]
    plans = check_plans_for_expiration(plans)
    assert plans[0].expired


@injection_test
def test_that_plans_are_only_set_to_expired_if_timeframe_is_expired(
    plan_generator: PlanGenerator,
):
    plan1 = plan_generator.create_plan(
        plan_creation_date=TestDatetimeService().now_minus_two_days(), timeframe=1
    )
    plan2 = plan_generator.create_plan(
        plan_creation_date=TestDatetimeService().now_minus_two_days(), timeframe=3
    )
    plans = [plan1, plan2]
    plans = check_plans_for_expiration(plans)
    assert plans[0].expired
    assert not plans[1].expired
