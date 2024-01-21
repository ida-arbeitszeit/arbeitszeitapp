from tests.data_generators import PlanGenerator

from .flask import ViewTestCase


class ToggleAvailability(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.plan_generator = self.injector.get(PlanGenerator)

    def test_trying_to_toggle_active_plan_results_in_302(self) -> None:
        company = self.login_company()
        plan = self.plan_generator.create_plan(planner=company.id)
        response = self.client.get(f"/company/toggle_availability/{plan}")
        assert response.status_code == 302
