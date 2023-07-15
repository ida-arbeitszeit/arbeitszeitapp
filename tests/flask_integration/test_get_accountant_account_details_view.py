from .flask import ViewTestCase


class GetAccountantAccountDetailsViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/accountant/account"

    def test_that_logged_in_accountant_receives_200(self) -> None:
        self.login_accountant()
        response = self.client.get(self.url)
        assert response.status_code == 200

    def test_that_response_contains_user_id(self) -> None:
        accountant = str(self.login_accountant())
        response = self.client.get(self.url)
        assert accountant in response.text
