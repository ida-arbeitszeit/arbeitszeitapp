from uuid import uuid4

from arbeitszeit.use_cases import ToggleProductAvailability

from .base_test_case import BaseTestCase


class UseCaseTester(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.toggle = self.injector.get(ToggleProductAvailability)

    def test_that_toggle_is_unsuccessful_when_plan_does_not_exist(self) -> None:
        response = self.toggle(uuid4(), uuid4())
        assert not response.is_success

    def test_that_toggle_is_unsuccessful_when_current_user_is_not_planner(self) -> None:
        plan = self.plan_generator.create_plan()
        response = self.toggle(uuid4(), plan.id)
        assert not response.is_success

    def test_that_toggling_returns_success_when_plan_exists_and_planner_is_current_user(
        self,
    ) -> None:
        plan = self.plan_generator.create_plan()
        response = self.toggle(plan.planner, plan.id)
        assert response.is_success

    def test_that_toggling_changes_availability_to_true(self) -> None:
        plan = self.plan_generator.create_plan()
        plan.is_available = False
        assert not plan.is_available
        self.toggle(plan.planner, plan.id)
        assert plan.is_available

    def test_that_toggling_changes_availability_to_false(self) -> None:
        plan = self.plan_generator.create_plan()
        assert plan.is_available
        self.toggle(plan.planner, plan.id)
        assert not plan.is_available
