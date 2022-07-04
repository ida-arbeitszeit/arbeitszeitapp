from .flask import ViewTestCase


class CompanyTests(ViewTestCase):
    def test_that_logged_in_company_get_200_response(self) -> None:
        self.company = self.login_company()
        response = self.client.get("/company/my_accounts")
        self.assertEqual(response.status_code, 200)
