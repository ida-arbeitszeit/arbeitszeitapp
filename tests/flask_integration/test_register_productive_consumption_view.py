from uuid import uuid4

from .flask import ViewTestCase


class CompanyGetTests(ViewTestCase):
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


class CompanyPostTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company()

    def test_that_logged_in_company_receives_400_when_posting_non_existing_plan_id(
        self,
    ) -> None:
        response = self.client.post(
            "/company/register_productive_consumption",
            data=dict(plan_id=str(uuid4()), amount=3, type_of_consumption="fixed"),
        )
        self.assertEqual(response.status_code, 400)

    def test_that_logged_in_company_receives_400_when_posting_invalid_type_of_consumption(
        self,
    ) -> None:
        response = self.client.post(
            "/company/register_productive_consumption",
            data=dict(
                plan_id=self.create_plan(), amount=3, type_of_consumption="unknown"
            ),
        )
        self.assertEqual(response.status_code, 400)

    def test_that_logged_in_company_receives_400_when_posting_incomplete_data(
        self,
    ) -> None:
        response = self.client.post(
            "/company/register_productive_consumption",
            data=dict(plan_id=self.create_plan(), amount=3),
        )
        self.assertEqual(response.status_code, 400)

    def test_that_logged_in_company_gets_redirected_when_posting_valid_data(
        self,
    ) -> None:
        response = self.client.post(
            "/company/register_productive_consumption",
            data=dict(
                plan_id=self.create_plan(), amount=3, type_of_consumption="fixed"
            ),
        )
        self.assertEqual(response.status_code, 302)

    def create_plan(self) -> str:
        return str(self.plan_generator.create_plan())
