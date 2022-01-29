from .flask import ViewTestCase


class CompanyViewTests(ViewTestCase):
    def test_requesting_view_as_company_results_in_200_status_code(self) -> None:
        self.company, _, self.email = self.login_company()
        self.company = self.confirm_company(company=self.company, email=self.email)
        response = self.client.get("/company/my_cooperations")
        self.assertEqual(response.status_code, 200)
