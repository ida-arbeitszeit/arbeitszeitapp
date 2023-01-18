from uuid import UUID, uuid4

from tests.data_generators import PlanGenerator

from .flask import ViewTestCase


class ViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.plan_generator = self.injector.get(PlanGenerator)

    def test_can_create_render_creation_page_from_existing_plan(self) -> None:
        company = self.login_company()
        plan = self.plan_generator.create_plan(planner=company.id)
        response = self.client.get(self._get_url(plan.id))
        self.assertEqual(response.status_code, 200)

    def test_get_404_for_from_non_existing_plan_id(self) -> None:
        self.login_company()
        response = self.client.get(self._get_url(uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_get_400_when_posting_random_form_data(self) -> None:
        company = self.login_company()
        plan = self.plan_generator.create_plan(planner=company.id)
        response = self.client.post(self._get_url(plan.id), data={"test": "1"})
        self.assertEqual(response.status_code, 400)

    def _get_url(self, plan: UUID) -> str:
        return f"/company/draft/from-plan/{plan}"
