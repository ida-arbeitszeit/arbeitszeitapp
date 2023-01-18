from uuid import UUID, uuid4

from tests.data_generators import PlanGenerator

from .flask import ViewTestCase


class DeleteDraftViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.plan_generator = self.injector.get(PlanGenerator)

    def test_get_405_when_getting_url_as_company(self) -> None:
        company = self.login_company()
        draft = self.plan_generator.draft_plan(planner=company.id)
        response = self.client.get(self.get_url(draft.id))
        self.assertEqual(response.status_code, 405)

    def test_get_404_when_posting_url_as_company_for_non_existing_draft(self) -> None:
        self.login_company()
        response = self.client.post(self.get_url(uuid4()))
        self.assertEqual(response.status_code, 404)

    def test_get_302_when_posting_url_as_company_for_existing_draft(self) -> None:
        company = self.login_company()
        draft = self.plan_generator.draft_plan(planner=company.id)
        response = self.client.post(self.get_url(draft.id))
        self.assertEqual(response.status_code, 302)

    def test_get_404_when_posting_draft_twice_as_company(self) -> None:
        company = self.login_company()
        draft = self.plan_generator.draft_plan(planner=company.id)
        self.client.post(self.get_url(draft.id))
        response = self.client.post(self.get_url(draft.id))
        self.assertEqual(response.status_code, 404)

    def get_url(self, draft_id: UUID) -> str:
        return f"/company/draft/delete/{draft_id}"
