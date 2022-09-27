from tests.data_generators import AccountantGenerator

from .flask import ViewTestCase


class LoginTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/accountant/login"
        self.accountant_generator = self.injector.get(AccountantGenerator)

    def test_get_200_when_accessing_login_view(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_200_when_posting_to_url(self) -> None:
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)

    def test_get_redirected_when_posting_correct_credentials(self) -> None:
        self.accountant_generator.create_accountant(
            email_address="a@b.c", password="testpassword"
        )
        response = self.client.post(
            self.url,
            data=dict(
                email="a@b.c",
                password="testpassword",
            ),
        )
        self.assertEqual(response.status_code, 302)
