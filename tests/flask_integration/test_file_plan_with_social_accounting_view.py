from uuid import UUID

from tests.data_generators import PlanGenerator

from .flask import ViewTestCase


class Tests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company()
        self.plan_generator = self.injector.get(PlanGenerator)

    def test_that_url_is_being_handled(self) -> None:
        draft = self.plan_generator.draft_plan()
        response = self.client.post(self.get_url(draft.id))
        self.assertNotEqual(response.status_code, 404)

    def test_that_we_get_redirected_when_posting_a_valid_draft(self) -> None:
        draft = self.plan_generator.draft_plan(planner=self.company)
        response = self.client.post(self.get_url(draft.id))
        self.assertEqual(response.status_code, 302)

    def test_that_we_get_cannot_post_twice_and_still_get_redirected(self) -> None:
        draft = self.plan_generator.draft_plan()
        self.client.post(self.get_url(draft.id))
        response = self.client.post(self.get_url(draft.id))
        self.assertGreaterEqual(response.status_code, 400)

    def get_url(self, draft: UUID) -> str:
        return f"/company/draft/{draft}/file_with_accounting"
