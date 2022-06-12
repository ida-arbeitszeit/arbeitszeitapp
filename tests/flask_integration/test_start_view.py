from .flask import ViewTestCase


class StartViewTests(ViewTestCase):
    def test_unauthorized_user_can_access_view(self) -> None:
        url = "/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
