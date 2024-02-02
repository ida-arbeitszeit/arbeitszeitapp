from typing import Optional

from parameterized import parameterized

from tests.flask_integration.flask import LogInUser, ViewTestCase


class UserAccessTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/user/statistics"

    @parameterized.expand(
        [
            (LogInUser.accountant, 200),
            (LogInUser.company, 200),
            (LogInUser.member, 200),
        ]
    )
    def test_get_200_for_logged_in_users(
        self, login: Optional[LogInUser], expected_code: int
    ) -> None:
        self.assert_response_has_expected_code(
            url=self.url,
            method="get",
            login=login,
            expected_code=expected_code,
        )

    def test_get_302_for_unauthenticated_users(self) -> None:
        self.assert_response_has_expected_code(
            url=self.url,
            method="get",
            login=None,
            expected_code=302,
        )
