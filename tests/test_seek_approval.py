from datetime import datetime

from arbeitszeit.use_cases import SeekApproval
from tests.data_generators import PlanGenerator
from tests.datetime_service import FakeDatetimeService
from tests.dependency_injection import injection_test


@injection_test
def test_that_any_plan_will_be_approved(
    plan_generator: PlanGenerator,
    seek_approval: SeekApproval,
):
    new_plan = plan_generator.create_plan()
    original_plan = plan_generator.create_plan()
    seek_approval(new_plan, original_plan)
    assert new_plan.approved


@injection_test
def test_that_any_plan_will_be_approved_and_original_plan_renewed(
    plan_generator: PlanGenerator,
    seek_approval: SeekApproval,
):
    new_plan = plan_generator.create_plan()
    original_plan = plan_generator.create_plan()
    seek_approval(new_plan, original_plan)
    assert new_plan.approved
    assert original_plan.renewed


@injection_test
def test_that_true_is_returned(
    plan_generator: PlanGenerator,
    seek_approval: SeekApproval,
):
    new_plan = plan_generator.create_plan()
    original_plan = plan_generator.create_plan()
    is_approval = seek_approval(new_plan, original_plan)
    assert is_approval is True


@injection_test
def test_that_approval_date_has_correct_day_of_month(
    plan_generator: PlanGenerator,
    seek_approval: SeekApproval,
    datetime_service: FakeDatetimeService,
):
    datetime_service.freeze_time(datetime(year=2021, month=5, day=3))
    new_plan = plan_generator.create_plan()
    original_plan = plan_generator.create_plan()
    seek_approval(new_plan, original_plan)
    assert new_plan.approval_date
    assert 3 == new_plan.approval_date.day
