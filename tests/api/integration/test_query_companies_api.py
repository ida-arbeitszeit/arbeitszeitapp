from tests.api.integration.base_test_case import ApiTestCase


class AnonymousUsersTests(ApiTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = self.url_prefix + "/companies"

    def test_anonymous_user_gets_status_code_401_on_get_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_anonymous_user_gets_corrrect_error_message_on_get_request(self):
        expected_message = "You have to authenticate before using this service."
        response = self.client.get(self.url)
        self.assertEqual(response.json["message"], expected_message)


class AuthenticatedCompanyTests(ApiTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.login_company()
        self.url = self.url_prefix + "/companies"

    def test_get_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)


class AuthenticatedMemberTests(ApiTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.login_member()
        self.url = self.url_prefix + "/companies"

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

    def test_get_returns_400_when_letters_are_in_offset_param(
        self,
    ):
        response = self.client.get(self.url + "?offset=abc")
        self.assertEqual(response.status_code, 400)

    def test_post_returns_405(self):
        response = self.client.post(self.url)
        self.assertEqual(response.mimetype, "application/json")
        self.assertEqual(response.status_code, 405)
