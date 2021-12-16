from datetime import datetime

from arbeitszeit.use_cases import HidePlan
from tests.data_generators import PlanGenerator

from .dependency_injection import injection_test


@injection_test
def test_that_correct_plan_gets_hidden_attribute_set_to_true(
    hide_plan: HidePlan,
    plan_generator: PlanGenerator,
):
    plan1 = plan_generator.create_plan()
    plan2 = plan_generator.create_plan()
    plan3 = plan_generator.create_plan()
    hide_plan(plan2.id)
    assert not plan1.hidden_by_user
    assert plan2.hidden_by_user
    assert not plan3.hidden_by_user


@injection_test
def test_that_correct_response_gets_returned(
    hide_plan: HidePlan,
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan()
    response = hide_plan(plan.id)
    assert response.plan_id == plan.id
    assert response.is_success == True


@injection_test
def test_that_active_plans_do_not_get_hidden_and_correct_response_gets_returned(
    hide_plan: HidePlan,
    plan_generator: PlanGenerator,
):
    plan = plan_generator.create_plan(activation_date=datetime.min)
    response = hide_plan(plan.id)
    assert response.plan_id == plan.id
    assert response.is_success == False
