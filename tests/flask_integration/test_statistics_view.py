from typing import Optional

from parameterized import parameterized

from tests.flask_integration.flask import LogInUser, ViewTestCase


class UserAccessTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()

    @parameterized.expand(
        [
            (LogInUser.accountant, 302),
            (None, 302),
            (LogInUser.company, 302),
            (LogInUser.member, 200),
        ]
    )
    def test_get_correct_response_from_member_page(
        self, login: Optional[LogInUser], expected_code: int
    ) -> None:
        self.assert_response_has_expected_code(
            url="/member/statistics",
            method="get",
            login=login,
            expected_code=expected_code,
        )

    @parameterized.expand(
        [
            (LogInUser.accountant, 302),
            (None, 302),
            (LogInUser.company, 200),
            (LogInUser.member, 302),
        ]
    )
    def test_get_correct_response_from_company_page(
        self, login: Optional[LogInUser], expected_code: int
    ) -> None:
        self.assert_response_has_expected_code(
            url="/company/statistics",
            method="get",
            login=login,
            expected_code=expected_code,
        )
