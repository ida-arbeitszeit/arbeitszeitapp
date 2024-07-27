from uuid import uuid4

from .flask import ViewTestCase


class CompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company()

    def test_that_logged_in_company_get_200_response(self) -> None:
        response = self.client.get("/company/register_productive_consumption")
        self.assertEqual(response.status_code, 200)

    def test_that_plan_id_from_query_string_appears_in_response_html(self) -> None:
        EXPECTED_PLAN_ID = uuid4()
        response = self.client.get(
            f"/company/register_productive_consumption?plan_id={EXPECTED_PLAN_ID}"
        )
        assert str(EXPECTED_PLAN_ID) in response.text

    def test_that_logged_in_company_receives_200_when_posting_valid_data(
        self,
    ) -> None:
        response = self.client.post(
            "/company/register_productive_consumption",
            data=dict(plan_id=str(uuid4()), amount=3, type_of_consumption="fixed"),
        )
        self.assertEqual(response.status_code, 200)

    def test_that_logged_in_company_receives_400_when_posting_invalid_data(
        self,
    ) -> None:
        response = self.client.post(
            "/company/register_productive_consumption",
            data=dict(plan_id="no uuid", amount=3, type_of_consumption="fixed"),
        )
        self.assertEqual(response.status_code, 400)
