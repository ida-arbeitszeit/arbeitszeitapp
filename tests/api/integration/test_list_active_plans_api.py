from tests.flask_integration.flask import ApiTestCase


class ListActivePlansTests(ApiTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = self.url_prefix + "/plans/active"

    def test_get_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(response.status_code, 200)

    def test_get_returns_200_with_correct_offset_param(self):
        response = self.client.get(self.url + "?offset=1")
        self.assertEqual(response.status_code, 200)

    def test_get_returns_200_with_correct_offset_and_limit_params(self):
        response = self.client.get(self.url + "?offset=1&limit=1")
        self.assertEqual(response.status_code, 200)

    def test_get_returns_400_with_letters_in_offset_param(self):
        response = self.client.get(self.url + "?offset=abc")
        self.assertEqual(response.status_code, 400)

    def test_post_returns_405(self):
        response = self.client.post(self.url)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(response.status_code, 405)

    def test_put_returns_405(self):
        response = self.client.put(self.url)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(response.status_code, 405)

    def test_patch_returns_405(self):
        response = self.client.patch(self.url)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(response.status_code, 405)

    def test_delete_returns_405(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(response.status_code, 405)
