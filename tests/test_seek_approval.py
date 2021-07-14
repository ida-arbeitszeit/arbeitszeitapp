from datetime import datetime, timedelta
from typing import Optional

from arbeitszeit.datetime_service import DatetimeService
from arbeitszeit.use_cases import seek_approval
from tests.data_generators import PlanGenerator, PlanRenewalGenerator
from tests.dependency_injection import injection_test


def now_minus_one_day() -> datetime:
    return datetime.now() - timedelta(days=1)


@injection_test
def test_that_any_plan_will_be_approved_if_it_is_not_a_plan_renewal(
    datetime_service: DatetimeService,
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan()
    seek_approval(datetime_service.now(), plan, None)
    assert plan.approved


@injection_test
def test_that_any_plan_will_be_approved_and_original_plan_renewed_if_it_is_a_plan_renewal_without_modifications(
    datetime_service: DatetimeService,
    plan_generator: PlanGenerator,
    plan_renewal_generator: Optional[PlanRenewalGenerator],
):
    plan = plan_generator.create_plan()
    original_plan = plan_generator.create_plan(plan_creation_date=now_minus_one_day())
    plan_renewal = plan_renewal_generator.create_plan_renewal(original_plan, False)
    seek_approval(datetime_service.now(), plan, plan_renewal)
    assert plan.approved
    assert plan_renewal.original_plan.renewed


@injection_test
def test_that_any_plan_will_be_approved_and_original_plan_renewed_if_it_is_a_plan_renewal_with_modifications(
    datetime_service: DatetimeService,
    plan_generator: PlanGenerator,
    plan_renewal_generator: Optional[PlanRenewalGenerator],
):
    plan = plan_generator.create_plan()
    original_plan = plan_generator.create_plan(plan_creation_date=now_minus_one_day())
    plan_renewal = plan_renewal_generator.create_plan_renewal(original_plan, True)
    seek_approval(datetime_service.now(), plan, plan_renewal)
    assert plan.approved
    assert plan_renewal.original_plan.renewed
