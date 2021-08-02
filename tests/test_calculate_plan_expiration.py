import datetime

import pytest

from arbeitszeit.use_cases import calculate_plan_expiration
from tests.data_generators import PlanGenerator
from tests.datetime_service import TestDatetimeService
from tests.dependency_injection import injection_test


@injection_test
def test_that_expiration_info_is_saved_as_instance_attributes(
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan()
    calculate_plan_expiration(plan)
    assert plan.expiration_relative
    assert len(plan.expiration_relative) == 3
    assert plan.expiration_date


@injection_test
def test_that_assertion_error_is_raised_when_plan_is_already_expired(
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan()
    plan.expired = True
    with pytest.raises(AssertionError, match="Plan is already expired"):
        calculate_plan_expiration(plan)


@injection_test
def test_that_relative_expiration_time_is_correctly_calculated(
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan(
        plan_creation_date=TestDatetimeService().now(), timeframe=1
    )
    calculate_plan_expiration(plan)
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
    calculate_plan_expiration(plan)
    calculated_expiration_date = (
        plan.expiration_date.strftime("%x") if plan.expiration_date else None
    )
    assert expected_expiration_date == calculated_expiration_date
