from .base_test_case import ViewTestCase


class CompanyViewTests(ViewTestCase):
    def test_requesting_view_as_company_results_in_200_status_code(self) -> None:
        self.login_company()
        response = self.client.get("/company/my_plans")
        self.assertEqual(response.status_code, 200)
