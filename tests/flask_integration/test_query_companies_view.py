from .flask import ViewTestCase


class CompanyViewTests(ViewTestCase):
    def test_that_logged_in_company_gets_200(self) -> None:
        self.company, _, self.email = self.login_company()
        self.company = self.confirm_company(company=self.company, email=self.email)
        response = self.client.get("/company/query_companies")
        self.assertEqual(response.status_code, 200)
