from .flask import ViewTestCase


class AccountantTestCase(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.login_accountant()
        self.url = "/accountant/plans/unreviewed"

    def test_can_access_view_with_200(self) -> None:
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
