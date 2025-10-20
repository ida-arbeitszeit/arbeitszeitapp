from typing import Optional

from parameterized import parameterized

from .base_test_case import LogInUser, ViewTestCase


class RedirectionTests(ViewTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.url = "/company/unconfirmed"

    @parameterized.expand(
        [
            (LogInUser.unconfirmed_company, 200),
            # any other case should result in a redirect
            (LogInUser.member, 302),
            (LogInUser.company, 302),
            (LogInUser.unconfirmed_member, 302),
            (LogInUser.accountant, 302),
            (None, 302),
        ]
    )
    def test_that_only_unconfirmed_companies_can_access_this_view(
        self, login: Optional[LogInUser], expected_code: int
    ) -> None:
        self.assert_response_has_expected_code(
            url=self.url, method="GET", expected_code=expected_code, login=login
        )
