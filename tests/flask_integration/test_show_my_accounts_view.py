from typing import Optional

from parameterized import parameterized

from .flask import LogInUser, ViewTestCase


class AuthTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/my_accounts"

    @parameterized.expand(
        [
            (LogInUser.accountant, 302),
            (None, 302),
            (LogInUser.company, 200),
            (LogInUser.member, 302),
        ]
    )
    def test_correct_status_codes_on_get_requests(
        self, login: Optional[LogInUser], expected_code: int
    ) -> None:
        self.assert_response_has_expected_code(
            url=self.url,
            method="get",
            login=login,
            expected_code=expected_code,
        )
