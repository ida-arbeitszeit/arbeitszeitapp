from .flask import ViewTestCase


class AuthenticatedAsAccountantTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.accountant = self.login_accountant()

    def test_get_200_response(self) -> None:
        response = self.client.get("/accountant/dashboard")
        self.assertEqual(response.status_code, 200)


class UnauthenticatedTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()

    def test_does_not_return_200_response(self) -> None:
        response = self.client.get("/accountant/dashboard")
        self.assertNotEqual(response.status_code, 200)


class AuthenticatedAsMemberTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.login_member()

    def test_does_not_return_200_response(self) -> None:
        response = self.client.get("/accountant/dashboard")
        self.assertNotEqual(response.status_code, 200)
