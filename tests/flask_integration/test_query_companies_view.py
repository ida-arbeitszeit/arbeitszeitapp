from .flask import ViewTestCase


class CompanyViewTests(ViewTestCase):
    def test_that_logged_in_company_gets_200(self) -> None:
        self.company = self.login_company()
        response = self.client.get("/company/query_companies")
        self.assertEqual(response.status_code, 200)
