from .flask import ViewTestCase


class CompanyViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company()

    def test_that_logged_in_company_gets_200(self) -> None:
        response = self.client.get("/company/query_companies")
        self.assertEqual(response.status_code, 200)

    def test_there_is_no_pagination_button_when_one_company_exists(self) -> None:
        self.company_generator.create_company()
        response = self.client.get("/company/query_companies")
        self.assertNotIn(r'class="pagination-link', response.text)

    def test_there_is_a_pagination_button_when_16_companies_exist(self) -> None:
        for _ in range(16):
            self.company_generator.create_company()
        response = self.client.get("/company/query_companies")
        self.assertIn(r'class="pagination-link', response.text)
