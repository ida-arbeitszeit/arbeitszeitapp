from uuid import UUID, uuid4

from tests.data_generators import PlanGenerator

from .flask import ViewTestCase


class ViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company()
        self.plan_generator = self.injector.get(PlanGenerator)

    def test_get_proper_response_code_with_correct_draft_id(self) -> None:
        draft = self.plan_generator.draft_plan(planner=self.company.id)
        response = self.client.get(self.get_url(draft.id))
        self.assertEqual(response.status_code, 200)

    def test_get_404_with_random_uuid(self) -> None:
        response = self.client.get(self.get_url(uuid4()))
        self.assertEqual(response.status_code, 404)

    def get_url(self, draft_id: UUID) -> str:
        return f"/company/draft/{draft_id}"
