from typing import Any

from parameterized import parameterized

from tests.api.integration.base_test_case import ApiTestCase, LogInUser


class AuthenticationTests(ApiTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = self.url_prefix + "/plans/active"

    @parameterized.expand(
        [
            (None, 401),
            (LogInUser.member, 200),
            (LogInUser.company, 200),
        ]
    )
    def test_only_authenticated_users_can_access_the_endpoint(
        self, user: LogInUser | None, expected_status_code: int
    ):
        if user:
            self.login_user(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, expected_status_code)

    def test_anonymous_user_gets_corrrect_error_message_on_get_request(self):
        expected_message = "You have to authenticate before using this service."
        response = self.client.get(self.url)
        self.assertEqual(response.json["message"], expected_message)

    def test_anonymous_user_gets_mimetype_application_json_on_get_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.mimetype, "application/json")


class AuthenticatedMemberTests(ApiTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = self.url_prefix + "/plans/active"
        self.login_member()

    def test_member_gets_status_code_405_on_post_request(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 405)

    @parameterized.expand(
        [(0, 0, 200), (1, 1, 200), (-1, 1, 400), (1, -1, 400), (1, "a", 400)]
    )
    def test_member_gets_correct_status_code_depending_on_limit_and_offset_params(
        self, limit: Any, offset: Any, expected_status_code: int
    ):
        response = self.client.get(
            self.url, query_string={"limit": limit, "offset": offset}
        )
        self.assertEqual(response.status_code, expected_status_code)
