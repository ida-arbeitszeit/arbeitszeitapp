from .flask import ViewTestCase


class ViewTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.company = self.login_company()

    def test_get_200_when_requesting_get(self) -> None:
        response = self.client.get(self.get_url())
        self.assertEqual(
            response.status_code,
            200,
        )

    def get_url(self) -> str:
        return "/company/draft"
