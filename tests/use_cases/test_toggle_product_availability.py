from uuid import uuid4

from arbeitszeit.use_cases import ToggleProductAvailability
from tests.data_generators import PlanGenerator

from .dependency_injection import injection_test


@injection_test
def test_that_toggle_is_unsuccessful_when_plan_does_not_exist(
    toggle: ToggleProductAvailability,
):
    response = toggle(uuid4())
    assert not response.is_success


@injection_test
def test_that_toggling_returns_success_with_existing_plan(
    toggle: ToggleProductAvailability, plan_generator: PlanGenerator
):
    plan = plan_generator.create_plan()
    response = toggle(plan.id)
    assert response.is_success


@injection_test
def test_that_toggling_changes_availability_to_true(
    toggle: ToggleProductAvailability, plan_generator: PlanGenerator
):
    plan = plan_generator.create_plan()
    plan.is_available = False
    assert not plan.is_available
    toggle(plan.id)
    assert plan.is_available


@injection_test
def test_that_toggling_changes_availability_to_false(
    toggle: ToggleProductAvailability, plan_generator: PlanGenerator
):
    plan = plan_generator.create_plan()
    assert plan.is_available
    toggle(plan.id)
    assert not plan.is_available
