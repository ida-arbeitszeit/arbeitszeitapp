from uuid import uuid4

from .view import ViewTestCase


class AuthenticatedMemberTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.login_member()

    def test_get_returns_200_status(self) -> None:
        response = self.client.get("/member/pay_consumer_product")
        self.assertEqual(response.status_code, 200)

    def test_posting_without_data_results_in_400(self) -> None:
        response = self.client.post("/member/pay_consumer_product")
        self.assertEqual(response.status_code, 400)

    def test_posting_with_invalid_form_data_results_in_400(self) -> None:
        response = self.client.post(
            "/member/pay_consumer_product",
            data=dict(
                plan_id=uuid4(),
                amount="abc",
            ),
        )
        self.assertEqual(response.status_code, 400)
