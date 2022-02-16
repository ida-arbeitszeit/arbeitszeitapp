from uuid import uuid4

from .flask import ViewTestCase


class CompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company, _, self.email = self.login_company()
        self.company = self.confirm_company(company=self.company, email=self.email)

    def test_that_logged_in_company_get_200_response(self) -> None:
        response = self.client.get("/company/transfer_to_company")
        self.assertEqual(response.status_code, 200)

    def test_that_logged_in_company_receives_200_when_posting_valid_data(
        self,
    ) -> None:
        response = self.client.post(
            "/company/transfer_to_company",
            data=dict(plan_id=str(uuid4()), amount=3, category="Fixed"),
        )
        self.assertEqual(response.status_code, 200)

    def test_that_logged_in_company_receives_400_when_posting_invalid_data(
        self,
    ) -> None:
        response = self.client.post(
            "/company/transfer_to_company",
            data=dict(plan_id="no uuid", amount=3, category="Fixed"),
        )
        self.assertEqual(response.status_code, 400)
