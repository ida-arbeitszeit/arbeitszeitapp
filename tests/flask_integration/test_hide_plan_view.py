from uuid import uuid4

from .base_test_case import ViewTestCase


class HidePlanViewTests(ViewTestCase):
    def test_that_trying_hide_existing_plan_returns_302(self) -> None:
        company = self.login_company()
        plan = self.plan_generator.create_plan(planner=company)
        response = self.client.post(f"/company/hide_plan/{plan}")
        assert response.status_code == 302

    def test_that_trying_hide_non_existing_plan_returns_302(self) -> None:
        response = self.client.post(f"/company/hide_plan/{uuid4()}")
        assert response.status_code == 302
