from arbeitszeit.use_cases import seek_approval
from tests.data_generators import PlanGenerator
from tests.datetime_service import TestDatetimeService
from tests.dependency_injection import injection_test


@injection_test
def test_that_any_plan_will_be_approved(
    plan_generator: PlanGenerator,
):
    new_plan = plan_generator.create_plan()
    original_plan = plan_generator.create_plan(
        plan_creation_date=TestDatetimeService().now_minus_one_day()
    )
    seek_approval(new_plan, original_plan)
    assert new_plan.approved


@injection_test
def test_that_any_plan_will_be_approved_and_original_plan_renewed(
    plan_generator: PlanGenerator,
):
    new_plan = plan_generator.create_plan()
    original_plan = plan_generator.create_plan(
        plan_creation_date=TestDatetimeService().now_minus_one_day()
    )
    seek_approval(new_plan, original_plan)
    assert new_plan.approved
    assert original_plan.renewed


@injection_test
def test_that_true_is_returned(
    plan_generator: PlanGenerator,
):
    new_plan = plan_generator.create_plan()
    original_plan = plan_generator.create_plan(
        plan_creation_date=TestDatetimeService().now_minus_one_day()
    )
    is_approval = seek_approval(new_plan, original_plan)
    assert is_approval is True


@injection_test
def test_that_approval_date_has_correct_day_of_month(
    plan_generator: PlanGenerator,
):
    new_plan = plan_generator.create_plan()
    original_plan = plan_generator.create_plan(
        plan_creation_date=TestDatetimeService().now_minus_one_day()
    )
    seek_approval(new_plan, original_plan)
    expected_day_of_month = TestDatetimeService().now().strftime("%d")
    day_of_month = new_plan.approval_date.strftime("%d")
    assert expected_day_of_month == day_of_month
