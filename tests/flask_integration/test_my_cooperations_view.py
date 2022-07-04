from .flask import ViewTestCase


class CompanyViewTests(ViewTestCase):
    def test_requesting_view_as_company_results_in_200_status_code(self) -> None:
        self.company = self.login_company()
        response = self.client.get("/company/my_cooperations")
        self.assertEqual(response.status_code, 200)
