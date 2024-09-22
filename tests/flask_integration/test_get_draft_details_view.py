from uuid import UUID, uuid4

from .flask import ViewTestCase


class ViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company()

    def test_get_proper_response_code_with_correct_draft_id(self) -> None:
        draft = self.plan_generator.draft_plan(planner=self.company.id)
        response = self.client.get(self.get_url(draft))
        self.assertEqual(response.status_code, 200)

    def test_get_404_with_random_uuid(self) -> None:
        response = self.client.get(self.get_url(uuid4()))
        self.assertEqual(response.status_code, 404)

    def get_url(self, draft_id: UUID) -> str:
        return f"/company/draft/{draft_id}"

    def test_post_404_with_random_uuid(self) -> None:
        response = self.client.post(self.get_url(uuid4()), data=self._valid_form_data())
        self.assertEqual(response.status_code, 404)

    def test_posting_invalid_data_results_in_400_error(self) -> None:
        response = self.client.post(self.get_url(uuid4()), data={})
        self.assertEqual(response.status_code, 400)

    def test_posting_valid_data_for_existing_plan_results_in_302(self) -> None:
        draft = self.plan_generator.draft_plan(planner=self.company.id)
        response = self.client.post(self.get_url(draft), data=self._valid_form_data())
        self.assertEqual(response.status_code, 302)

    def _valid_form_data(self) -> dict[str, str]:
        return dict(
            prd_name="test name",
            description="test description",
            timeframe="1",
            prd_unit="test unit",
            prd_amount="12",
            costs_p="1",
            costs_r="1",
            costs_a="1",
            productive_or_public="y",
        )
