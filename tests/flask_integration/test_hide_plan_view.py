from uuid import uuid4

from tests.data_generators import PlanGenerator

from .flask import ViewTestCase


class HidePlanViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.plan_generator = self.injector.get(PlanGenerator)

    def test_that_trying_hide_existing_plan_returns_302(self) -> None:
        company = self.login_company()
        plan = self.plan_generator.create_plan(planner=company.id)
        response = self.client.post(f"/company/hide_plan/{plan.id}")
        assert response.status_code == 302

    def test_that_trying_hide_non_existing_plan_returns_302(self) -> None:
        response = self.client.post(f"/company/hide_plan/{uuid4()}")
        assert response.status_code == 302
