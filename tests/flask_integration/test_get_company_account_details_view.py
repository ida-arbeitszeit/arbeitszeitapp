from .flask import ViewTestCase


class GetCompanyAccountDetailsViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/account"

    def test_that_logged_in_company_receives_200(self) -> None:
        self.login_company()
        response = self.client.get(self.url)
        assert response.status_code == 200

    def test_that_response_contains_user_id(self) -> None:
        company = str(self.login_company().id)
        response = self.client.get(self.url)
        assert company in response.text
