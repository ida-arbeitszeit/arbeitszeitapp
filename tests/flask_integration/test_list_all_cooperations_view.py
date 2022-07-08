from .flask import ViewTestCase


class CompanyViewTests(ViewTestCase):
    def test_that_requesting_view_results_200_status_code(self) -> None:
        self.company = self.login_company()
        response = self.client.get("/company/list_all_cooperations")
        self.assertEqual(response.status_code, 200)
