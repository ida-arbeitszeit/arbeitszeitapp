from typing import Optional

from parameterized import parameterized

from .base_test_case import LogInUser, ViewTestCase


class UserAccessTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/"

    @parameterized.expand(
        [
            (LogInUser.accountant, 200),
            (None, 200),
            (LogInUser.company, 200),
            (LogInUser.member, 200),
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
