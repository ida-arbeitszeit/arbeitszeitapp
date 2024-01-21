from uuid import UUID

from tests.data_generators import PlanGenerator

from .flask import ViewTestCase


class ViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.plan_generator = self.injector.get(PlanGenerator)
        self.company = self.login_company()

    def test_can_create_render_creation_page_from_existing_plan(self) -> None:
        plan = self.plan_generator.create_plan(planner=self.company.id)
        response = self.client.post(self._get_url(plan))
        self.assertEqual(response.status_code, 302)

    def test_get_405_method_not_allowed_when_trying_to_get_the_route(self) -> None:
        plan = self.plan_generator.create_plan(planner=self.company.id)
        response = self.client.get(self._get_url(plan))
        self.assertEqual(response.status_code, 405)

    def _get_url(self, plan: UUID) -> str:
        return f"/company/draft/from-plan/{plan}"
