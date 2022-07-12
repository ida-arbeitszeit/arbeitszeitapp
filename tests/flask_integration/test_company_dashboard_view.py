from tests.flask_integration.flask import ViewTestCase


class AuthenticatedCompanyTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company()
        self.url = "/company/dashboard"

    def test_get_200(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
