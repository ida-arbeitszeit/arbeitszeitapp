from .flask import ViewTestCase


class CompanyViewTests(ViewTestCase):
    def test_that_requesting_view_results_200_status_code(self) -> None:
        self.company, _, self.email = self.login_company()
        self.company = self.confirm_company(company=self.company, email=self.email)
        response = self.client.get("/company/list_all_cooperations")
        self.assertEqual(response.status_code, 200)
